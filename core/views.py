from django.db.models import Count, Q
from django.shortcuts import render

from articles.models import Article
from interactions.models import Reaction

PUBLIC_NEWS_ORDERING = ("-published_at", "-created_at", "-id")
TOP_NEWS_ORDERING = ("-likes_count", "-published_at", "-created_at", "-id")


def home(request):
    Article.sanitize_published_timestamps()
    published = (
        Article.objects.filter(status=Article.STATUS_PUBLISHED)
        .select_related("author")
        .prefetch_related("categories", "tags")
    )

    main_featured = (
        published.filter(is_featured=True).order_by(*PUBLIC_NEWS_ORDERING).first()
        or published.order_by(*PUBLIC_NEWS_ORDERING).first()
    )

    top_items = (
        published.annotate(
            likes_count=Count(
                "reactions",
                filter=Q(reactions__type=Reaction.TYPE_LIKE),
            )
        )
        .order_by(*TOP_NEWS_ORDERING)[:6]
    )

    latest_qs = published.order_by(*PUBLIC_NEWS_ORDERING)
    if main_featured:
        latest_qs = latest_qs.exclude(pk=main_featured.pk)
    latest_news = latest_qs[:6]

    return render(
        request,
        "core/home.html",
        {
            "main_featured": main_featured,
            "top_items": top_items,
            "latest_news": latest_news,
            "page_title": "Главная",
            "page_description": "KZ Arena: новости спорта и киберспорта Казахстана.",
            "breadcrumbs": [],
        },
    )


def about(request):
    return render(
        request,
        "core/about.html",
        {
            "page_title": "О проекте",
            "page_description": "Что такое KZ Arena и для кого мы его создаем.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "О проекте", "url": None},
            ],
        },
    )


def custom_404(request, exception):
    return render(request, "core/404.html", status=404)


def custom_500(request):
    return render(request, "core/500.html", status=500)
