from django.shortcuts import render

from articles.models import Article


def home(request):
    published = Article.objects.filter(status=Article.STATUS_PUBLISHED).select_related("author").prefetch_related("categories", "tags")

    main_featured = published.filter(is_featured=True).order_by("-published_at").first() or published.order_by("-published_at").first()

    top_qs = published.order_by("-views_count", "-published_at")
    if main_featured:
        top_qs = top_qs.exclude(pk=main_featured.pk)
    top_items = top_qs[:5]

    latest_qs = published.order_by("-published_at")
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
