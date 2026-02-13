from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from articles.models import Article
from teams.models import Team

from .models import Match, Tournament


def tournament_list(request):
    queryset = Tournament.objects.prefetch_related("matches").order_by("-start_date")

    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()

    if kind in {Tournament.KIND_SPORT, Tournament.KIND_ESPORT}:
        queryset = queryset.filter(kind=kind)

    valid_disciplines = {choice[0] for choice in Tournament.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    paginator = Paginator(queryset, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "tournaments/tournament_list.html",
        {
            "page_title": "Турниры",
            "page_description": "Актуальные и предстоящие турниры по видам спорта и киберспорта.",
            "page_obj": page_obj,
            "current_filters": {
                "kind": kind,
                "discipline": discipline,
            },
            "pagination_query": query_params.urlencode(),
            "discipline_choices": Tournament.DISCIPLINE_CHOICES,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Турниры", "url": None},
            ],
        },
    )


def tournament_detail(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)

    matches = (
        tournament.matches.select_related("team_a", "team_b", "result")
        .order_by("datetime")
    )

    related_articles = (
        Article.objects.filter(
            status=Article.STATUS_PUBLISHED,
            discipline=tournament.discipline,
        )
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-published_at")[:4]
        if tournament.discipline
        else Article.objects.none()
    )

    return render(
        request,
        "tournaments/tournament_detail.html",
        {
            "tournament": tournament,
            "matches": matches,
            "related_articles": related_articles,
            "page_title": tournament.name,
            "page_description": f"{tournament.get_kind_display()} турнир {tournament.name}",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Турниры", "url": "tournaments:tournament_list"},
                {"label": tournament.name, "url": None},
            ],
        },
    )


def match_list(request):
    now = timezone.now()
    queryset = (
        Match.objects.filter(datetime__gte=now)
        .select_related("team_a", "team_b", "tournament", "result")
        .order_by("datetime")
    )

    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()
    status = request.GET.get("status", "").strip()

    if kind in {Tournament.KIND_SPORT, Tournament.KIND_ESPORT}:
        queryset = queryset.filter(tournament__kind=kind)

    valid_disciplines = {choice[0] for choice in Tournament.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(tournament__discipline=discipline)

    valid_statuses = {choice[0] for choice in Match.STATUS_CHOICES}
    if status in valid_statuses:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    page_matches = list(page_obj.object_list)
    live_matches = [match for match in page_matches if match.status == Match.STATUS_LIVE]
    scheduled_matches = [match for match in page_matches if match.status == Match.STATUS_SCHEDULED]
    finished_matches = [match for match in page_matches if match.status == Match.STATUS_FINISHED]

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "tournaments/match_list.html",
        {
            "page_title": "Матчи",
            "page_description": "Ближайшие матчи, результаты и статус в реальном времени.",
            "page_obj": page_obj,
            "live_matches": live_matches,
            "scheduled_matches": scheduled_matches,
            "finished_matches": finished_matches,
            "has_active_filters": any([kind, discipline, status]),
            "current_filters": {
                "kind": kind,
                "discipline": discipline,
                "status": status,
            },
            "discipline_choices": Tournament.DISCIPLINE_CHOICES,
            "status_choices": Match.STATUS_CHOICES,
            "pagination_query": query_params.urlencode(),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Матчи", "url": None},
            ],
        },
    )


def match_detail(request, pk):
    match = get_object_or_404(
        Match.objects.select_related("team_a", "team_b", "tournament", "result"),
        pk=pk,
    )

    related_articles = (
        Article.objects.filter(
            status=Article.STATUS_PUBLISHED,
            discipline=match.tournament.discipline,
        )
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-published_at")[:4]
        if match.tournament.discipline
        else Article.objects.none()
    )

    return render(
        request,
        "tournaments/match_detail.html",
        {
            "match": match,
            "related_articles": related_articles,
            "page_title": f"{match.team_a.name} vs {match.team_b.name}",
            "page_description": "Детальная информация о матче.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Матчи", "url": "matches:match_list"},
                {"label": f"{match.team_a.name} vs {match.team_b.name}", "url": None},
            ],
        },
    )
