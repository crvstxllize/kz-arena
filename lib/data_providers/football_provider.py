from datetime import datetime, timezone
from typing import List

from .cache import get_cached, set_cached
from .http_utils import fetch_json
from .types import MatchEntity, ProviderResult, TeamEntity, TournamentEntity


class FootballProvider:
    cache_key = "provider:football"
    ttl_minutes = 20
    league_name = "Kazakhstan Premier League"
    source_url = "https://www.thesportsdb.com/"

    def fetch(self) -> ProviderResult:
        cached = get_cached(self.cache_key, self.ttl_minutes)
        if cached:
            return cached

        fetched_at = datetime.now(timezone.utc)
        try:
            teams_payload = fetch_json(
                "https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php",
                params={"l": self.league_name},
            )
            teams_raw = teams_payload.get("teams") or []

            teams: List[TeamEntity] = []
            for team in teams_raw:
                name = (team.get("strTeam") or "").strip()
                if not name:
                    continue
                teams.append(
                    TeamEntity(
                        id=f"football-{team.get('idTeam') or name.lower().replace(' ', '-')}",
                        name=name,
                        discipline="football",
                        country=team.get("strCountry") or "Kazakhstan",
                        city=team.get("strStadiumLocation") or "",
                        logo=team.get("strBadge") or "",
                        source_url=team.get("strWebsite") or self.source_url,
                        updated_at=fetched_at,
                    )
                )

            # TheSportsDB next-events endpoint is not always league-stable for this league id.
            # To avoid false statements, provider returns only teams from API and leaves match schedule to fallback.
            tournaments = [
                TournamentEntity(
                    id="football-kpl",
                    name="Kazakhstan Premier League",
                    discipline="football",
                    tier="National",
                    location="Kazakhstan",
                    start_date=None,
                    end_date=None,
                    status="upcoming",
                    source_url=self.source_url,
                    updated_at=fetched_at,
                )
            ]

            result = ProviderResult(
                teams=teams,
                tournaments=tournaments,
                matches=[],
                is_fallback=False if teams else True,
                fetched_at=fetched_at,
                sources=[self.source_url],
            )
        except Exception:
            result = ProviderResult(
                teams=[],
                tournaments=[],
                matches=[],
                is_fallback=True,
                fetched_at=fetched_at,
                sources=[self.source_url],
            )

        set_cached(self.cache_key, result)
        return result
