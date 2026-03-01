from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from articles.models import Article
from tournaments.models import Match

from .models import Team

FEATURED_TEAM_KEYS = (
    ("астана", "astana", "fc-astana"),
    ("кайрат", "kairat", "fc-kairat", "kairat-almaty"),
    ("novaq",),
    ("golden-barys",),
)
EXAMPLE_TEAMS_LIMIT = 6


def _normalize_team_key(value):
    return (value or "").strip().lower()


def _is_featured_team(team):
    team_keys = {_normalize_team_key(team.slug), _normalize_team_key(team.name)}
    for featured_keys in FEATURED_TEAM_KEYS:
        if team_keys.intersection({_normalize_team_key(item) for item in featured_keys}):
            return True
    return False


def _featured_team_rank(team):
    team_keys = {_normalize_team_key(team.slug), _normalize_team_key(team.name)}
    for index, featured_keys in enumerate(FEATURED_TEAM_KEYS):
        if team_keys.intersection({_normalize_team_key(item) for item in featured_keys}):
            return index
    return len(FEATURED_TEAM_KEYS)


def _decorate_team(team, is_example):
    team.is_example = is_example
    team.display_name = f"Пример: {team.name}" if is_example else team.name
    return team


def _build_public_team_collection(queryset):
    teams = [team for team in queryset if team.players.all()]
    featured = sorted(
        [team for team in teams if _is_featured_team(team)],
        key=lambda item: (_featured_team_rank(item), item.name.lower(), item.id),
    )
    featured_ids = {team.id for team in featured}
    examples = sorted(
        [team for team in teams if team.id not in featured_ids],
        key=lambda item: (item.name.lower(), item.id),
    )[:EXAMPLE_TEAMS_LIMIT]

    decorated = [_decorate_team(team, is_example=False) for team in featured]
    decorated.extend(_decorate_team(team, is_example=True) for team in examples)
    return decorated


def team_list(request):
    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()
    queryset = Team.objects.filter(is_active=True).prefetch_related("players").order_by("name")

    if kind in {Team.KIND_SPORT, Team.KIND_ESPORT}:
        queryset = queryset.filter(kind=kind)

    valid_disciplines = {choice[0] for choice in Team.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    public_teams = _build_public_team_collection(queryset)
    paginator = Paginator(public_teams, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "teams/team_list.html",
        {
            "page_title": "Команды",
            "page_description": "Составы команд и ключевые показатели по сезону.",
            "page_obj": page_obj,
            "current_filters": {
                "kind": kind,
                "discipline": discipline,
            },
            "pagination_query": query_params.urlencode(),
            "discipline_choices": Team.DISCIPLINE_CHOICES,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Команды", "url": None},
            ],
        },
    )


def team_detail(request, slug):
    team = get_object_or_404(Team.objects.prefetch_related("players"), slug=slug, is_active=True)
    _decorate_team(team, is_example=not _is_featured_team(team))
    now = timezone.now()
    team_name = (team.name or "").strip()

    upcoming_matches = (
        Match.objects.filter(
            Q(status=Match.STATUS_UPCOMING),
            Q(start_datetime__gte=now),
            Q(home_team=team)
            | Q(away_team=team)
            | Q(home_team__name__iexact=team_name)
            | Q(away_team__name__iexact=team_name),
        )
        .select_related("home_team", "away_team", "tournament")
        .order_by("start_datetime")[:5]
    )

    related_articles = (
        Article.objects.filter(
            status=Article.STATUS_PUBLISHED,
            discipline=team.discipline,
        )
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-published_at")[:4]
        if team.discipline
        else Article.objects.none()
    )

    return render(
        request,
        "teams/team_detail.html",
        {
            "team": team,
            "upcoming_matches": upcoming_matches,
            "related_articles": related_articles,
            "page_title": team.name,
            "page_description": team.description or team.name,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Команды", "url": "teams:team_list"},
                {"label": team.name, "url": None},
            ],
        },
    )
