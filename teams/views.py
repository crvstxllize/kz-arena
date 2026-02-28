from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from articles.models import Article
from lib.data_sync import refresh_sports_data
from tournaments.models import Match

from .models import Team


def team_list(request):
    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()

    manual_queryset = (
        Team.objects.filter(is_manual=True, is_active=True).prefetch_related("players").order_by("name")
    )
    is_demo_mode = not manual_queryset.exists()

    if is_demo_mode:
        data_meta = refresh_sports_data()
        queryset = (
            Team.objects.filter(is_manual=False, is_active=True)
            .prefetch_related("players")
            .order_by("name")
        )
    else:
        data_meta = None
        queryset = manual_queryset

    if kind in {Team.KIND_SPORT, Team.KIND_ESPORT}:
        queryset = queryset.filter(kind=kind)

    valid_disciplines = {choice[0] for choice in Team.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    paginator = Paginator(queryset, 12)
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
            "data_meta": data_meta,
            "is_demo_mode": is_demo_mode,
        },
    )


def team_detail(request, slug):
    data_meta = refresh_sports_data()
    team = get_object_or_404(Team.objects.prefetch_related("players"), slug=slug, is_active=True)
    now = timezone.now()
    team_name = (team.name or "").strip()

    upcoming_matches = (
        Match.objects.filter(
            Q(datetime__gte=now),
            Q(team_a=team)
            | Q(team_b=team)
            | Q(team_a__name__iexact=team_name)
            | Q(team_b__name__iexact=team_name),
        )
        .select_related("team_a", "team_b", "tournament", "result")
        .order_by("datetime")[:8]
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
            "data_meta": data_meta,
        },
    )
