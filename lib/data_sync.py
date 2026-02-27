from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone as dj_timezone

from teams.models import Team
from tournaments.models import Match, MatchResult, Tournament

from .data_providers import BasketballProvider, EsportsProvider, FootballProvider
from .data_providers.fallback_data import (
    FALLBACK_MATCHES,
    FALLBACK_SOURCES,
    FALLBACK_TEAMS,
    FALLBACK_TOURNAMENTS,
)
from .data_providers.types import MatchEntity, TeamEntity, TournamentEntity

CACHE_KEY = "sports_data_sync_meta_v1"
CACHE_TTL_SECONDS = 60 * 20


def _kind_by_discipline(discipline: str):
    if discipline in {"football", "basketball"}:
        return "sport"
    return "esport"


def _to_aware(dt: Optional[datetime]):
    if dt is None:
        return None
    if dj_timezone.is_naive(dt):
        return dj_timezone.make_aware(dt)
    return dt


def _status_to_model(status: str):
    if status == "live":
        return Match.STATUS_LIVE
    if status == "finished":
        return Match.STATUS_FINISHED
    return Match.STATUS_SCHEDULED


def _merge_results():
    providers = [FootballProvider(), BasketballProvider(), EsportsProvider()]
    provider_results = [provider.fetch() for provider in providers]

    teams: List[TeamEntity] = []
    tournaments: List[TournamentEntity] = []
    matches: List[MatchEntity] = []
    sources: List[str] = []
    fallback = False

    for result in provider_results:
        teams.extend(result.teams)
        tournaments.extend(result.tournaments)
        matches.extend(result.matches)
        sources.extend(result.sources)
        fallback = fallback or result.is_fallback

    # If schedule data is incomplete, fallback ensures UI still has consistent cards.
    if not matches:
        fallback = True
        teams.extend(FALLBACK_TEAMS)
        tournaments.extend(FALLBACK_TOURNAMENTS)
        matches.extend(FALLBACK_MATCHES)
        sources.extend(FALLBACK_SOURCES)

    # Deduplicate by id preserving first occurrence.
    teams_map = {item.id: item for item in teams}
    tournaments_map = {item.id: item for item in tournaments}
    matches_map = {item.id: item for item in matches}

    fetched_at = datetime.now(timezone.utc)
    return (
        list(teams_map.values()),
        list(tournaments_map.values()),
        list(matches_map.values()),
        sorted(set(sources)),
        fallback,
        fetched_at,
    )


@transaction.atomic
def refresh_sports_data(force: bool = False):
    if not force:
        cached = cache.get(CACHE_KEY)
        if cached:
            return cached

    teams, tournaments, matches, sources, is_fallback, fetched_at = _merge_results()

    teams_by_name: Dict[str, Team] = {}
    for item in teams:
        team, _ = Team.objects.get_or_create(
            name=item.name,
            defaults={
                "kind": _kind_by_discipline(item.discipline),
                "discipline": (
                    item.discipline if item.discipline in dict(Team.DISCIPLINE_CHOICES) else ""
                ),
                "country": item.country or "Kazakhstan",
            },
        )
        team.kind = _kind_by_discipline(item.discipline)
        team.discipline = (
            item.discipline if item.discipline in dict(Team.DISCIPLINE_CHOICES) else ""
        )
        team.country = item.country or "Kazakhstan"
        team.city = item.city or ""
        team.source_url = item.source_url or ""
        team.source_updated_at = _to_aware(item.updated_at)
        team.save()
        teams_by_name[item.name] = team

    tournaments_by_ext: Dict[str, Tournament] = {}
    for item in tournaments:
        start = item.start_date.date() if item.start_date else dj_timezone.now().date()
        end = item.end_date.date() if item.end_date else start
        tournament, _ = Tournament.objects.get_or_create(
            name=item.name,
            defaults={
                "kind": _kind_by_discipline(item.discipline),
                "discipline": (
                    item.discipline
                    if item.discipline in dict(Tournament.DISCIPLINE_CHOICES)
                    else ""
                ),
                "location": item.location or "",
                "start_date": start,
                "end_date": end,
            },
        )
        tournament.kind = _kind_by_discipline(item.discipline)
        tournament.discipline = (
            item.discipline if item.discipline in dict(Tournament.DISCIPLINE_CHOICES) else ""
        )
        tournament.location = item.location or ""
        tournament.start_date = start
        tournament.end_date = end
        tournament.source_url = item.source_url or ""
        tournament.source_updated_at = _to_aware(item.updated_at)
        tournament.save()
        tournaments_by_ext[item.id] = tournament
        tournaments_by_ext[item.name] = tournament

    for item in matches:
        team_a = teams_by_name.get(item.team_a)
        team_b = teams_by_name.get(item.team_b)
        tournament = tournaments_by_ext.get(item.tournament_id)
        if not tournament:
            tournament = tournaments_by_ext.get(item.tournament_id.replace("-", " ").title())
        if not team_a or not team_b or not tournament:
            continue

        start_time = _to_aware(item.start_time) or dj_timezone.now()
        match, _ = Match.objects.get_or_create(
            tournament=tournament,
            team_a=team_a,
            team_b=team_b,
            datetime=start_time,
            defaults={"stage": "", "status": _status_to_model(item.status)},
        )
        match.status = _status_to_model(item.status)
        match.stream_url = item.stream_url or ""
        match.source_url = item.source_url or tournament.source_url or ""
        match.source_updated_at = _to_aware(item.updated_at)
        match.save()

        if item.score and ":" in item.score:
            left, right = [part.strip() for part in item.score.split(":", 1)]
            if left.isdigit() and right.isdigit():
                a_score = int(left)
                b_score = int(right)
                winner = None
                if a_score > b_score:
                    winner = team_a
                elif b_score > a_score:
                    winner = team_b
                MatchResult.objects.update_or_create(
                    match=match,
                    defaults={"score_a": a_score, "score_b": b_score, "winner": winner},
                )

    meta = {
        "is_fallback": is_fallback,
        "fetched_at": fetched_at,
        "sources": sources,
    }
    cache.set(CACHE_KEY, meta, CACHE_TTL_SECONDS)
    return meta


def get_data_meta():
    return cache.get(CACHE_KEY) or {"is_fallback": True, "fetched_at": None, "sources": []}
