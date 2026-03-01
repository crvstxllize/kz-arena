from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from articles.models import Article

from .models import Match, Tournament


def tournament_list(request):
    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()
    queryset = Tournament.objects.prefetch_related("matches").order_by("-start_date", "-created_at")

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

    matches = tournament.matches.select_related("home_team", "away_team").order_by("start_datetime")

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
    queryset = Match.objects.select_related("home_team", "away_team", "tournament")

    category = request.GET.get("category", request.GET.get("kind", "")).strip()
    discipline = request.GET.get("discipline", "").strip()
    status = request.GET.get("status", "").strip()

    if category in {Tournament.KIND_SPORT, Tournament.KIND_ESPORT}:
        queryset = queryset.filter(kind=category)

    valid_disciplines = {choice[0] for choice in Tournament.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    valid_statuses = {choice[0] for choice in Match.STATUS_CHOICES}
    if status in valid_statuses:
        queryset = queryset.filter(status=status)

    live_matches = queryset.filter(status=Match.STATUS_LIVE).order_by("start_datetime")
    upcoming_matches = queryset.filter(status=Match.STATUS_UPCOMING).order_by("start_datetime")
    finished_matches = queryset.filter(status=Match.STATUS_FINISHED).order_by("-start_datetime")
    all_matches = list(live_matches) + list(upcoming_matches) + list(finished_matches)

    return render(
        request,
        "tournaments/match_list.html",
        {
            "page_title": "Матчи",
            "page_description": "Матчи и результаты по спортивным и киберспортивным дисциплинам.",
            "page_obj": {"object_list": all_matches},
            "live_matches": live_matches,
            "upcoming_matches": upcoming_matches,
            "finished_matches": finished_matches,
            "has_active_filters": any([category, discipline, status]),
            "current_filters": {
                "category": category,
                "discipline": discipline,
                "status": status,
            },
            "discipline_choices": Tournament.DISCIPLINE_CHOICES,
            "status_choices": Match.STATUS_CHOICES,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Матчи", "url": None},
            ],
        },
    )


def match_detail(request, pk):
    match = get_object_or_404(
        Match.objects.select_related("home_team", "away_team", "tournament"),
        pk=pk,
    )

    related_articles = (
        Article.objects.filter(
            status=Article.STATUS_PUBLISHED,
            discipline=match.discipline or (match.tournament.discipline if match.tournament_id else ""),
        )
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-published_at")[:4]
        if match.discipline or (match.tournament_id and match.tournament.discipline)
        else Article.objects.none()
    )

    return render(
        request,
        "tournaments/match_detail.html",
        {
            "match": match,
            "related_articles": related_articles,
            "page_title": match.participants_display,
            "page_description": "Детальная информация о матче.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Матчи", "url": "matches:match_list"},
                {"label": match.participants_display, "url": None},
            ],
        },
    )
