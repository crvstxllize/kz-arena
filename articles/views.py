from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from comments.models import Comment
from interactions.models import ArticleRating, Favorite, Reaction, Subscription
from taxonomy.models import Category, Tag

from .models import Article


def _base_published_queryset():
    return (
        Article.objects.filter(status=Article.STATUS_PUBLISHED)
        .select_related("author")
        .prefetch_related("categories", "tags")
    )


def news_list(request):
    queryset = _base_published_queryset()

    q = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    ordering = request.GET.get("ordering", "new").strip() or "new"

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(content__icontains=q)
            | Q(author__username__icontains=q)
        )

    if kind in {Article.KIND_SPORT, Article.KIND_ESPORT}:
        queryset = queryset.filter(kind=kind)

    valid_disciplines = {choice[0] for choice in Article.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    if category_slug:
        queryset = queryset.filter(categories__slug=category_slug)

    if tag_slug:
        queryset = queryset.filter(tags__slug=tag_slug)

    if ordering == "popular":
        queryset = queryset.order_by("-views_count", "-published_at", "-id")
    else:
        ordering = "new"
        queryset = queryset.order_by("-published_at", "-id")

    queryset = queryset.distinct()

    featured = (
        _base_published_queryset().filter(is_featured=True).order_by("-published_at").first()
        or _base_published_queryset().order_by("-published_at").first()
    )

    top_items_qs = _base_published_queryset().order_by("-views_count", "-published_at")
    if featured:
        top_items_qs = top_items_qs.exclude(pk=featured.pk)
    top_items = list(top_items_qs[:5])

    paginator = Paginator(queryset, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)
    pagination_query = query_params.urlencode()

    current_filters = {
        "q": q,
        "kind": kind,
        "discipline": discipline,
        "category": category_slug,
        "tag": tag_slug,
        "ordering": ordering,
    }

    return render(
        request,
        "articles/news_list.html",
        {
            "page_title": "Новости",
            "page_description": "Главные новости спорта и киберспорта Казахстана.",
            "featured": featured,
            "top_items": top_items,
            "page_obj": page_obj,
            "categories": Category.objects.order_by("name"),
            "tags": Tag.objects.order_by("name"),
            "current_filters": current_filters,
            "pagination_query": pagination_query,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Новости", "url": None},
            ],
        },
    )


def news_detail(request, slug):
    article = get_object_or_404(
        _base_published_queryset(),
        slug=slug,
    )

    view_key = f"viewed_article_{article.pk}"
    if not request.session.get(view_key):
        Article.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
        request.session[view_key] = True
        article.refresh_from_db(fields=["views_count"])

    related = _base_published_queryset().exclude(pk=article.pk)
    if article.discipline:
        related = related.filter(discipline=article.discipline)
    elif article.categories.exists():
        related = related.filter(categories__in=article.categories.all())

    related_items = related.distinct().order_by("-published_at")[:4]

    reaction_counts = Reaction.objects.filter(article=article).aggregate(
        likes=Count("id", filter=Q(type=Reaction.TYPE_LIKE)),
        dislikes=Count("id", filter=Q(type=Reaction.TYPE_DISLIKE)),
    )

    user_reaction = None
    user_favorited = False
    user_rating = None
    primary_category = article.categories.first()
    user_category_subscribed = False

    if request.user.is_authenticated:
        user_reaction_obj = Reaction.objects.filter(article=article, user=request.user).first()
        if user_reaction_obj:
            user_reaction = user_reaction_obj.type

        user_favorited = Favorite.objects.filter(article=article, user=request.user).exists()
        user_rating = (
            ArticleRating.objects.filter(article=article, user=request.user)
            .values_list("value", flat=True)
            .first()
        )

        if primary_category:
            user_category_subscribed = Subscription.objects.filter(
                user=request.user,
                category=primary_category,
            ).exists()

    comments = Comment.objects.filter(article=article, is_approved=True).select_related("user")
    rating_stats = ArticleRating.objects.filter(article=article).aggregate(
        average=Avg("value"),
        count=Count("id"),
    )

    return render(
        request,
        "articles/news_detail.html",
        {
            "article": article,
            "related_items": related_items,
            "reaction_counts": {
                "likes": reaction_counts["likes"] or 0,
                "dislikes": reaction_counts["dislikes"] or 0,
            },
            "favorites_count": Favorite.objects.filter(article=article).count(),
            "user_reaction": user_reaction,
            "user_favorited": user_favorited,
            "user_rating": user_rating,
            "primary_category": primary_category,
            "user_category_subscribed": user_category_subscribed,
            "rating_summary": {
                "average": (
                    round(float(rating_stats["average"]), 2)
                    if rating_stats["average"] is not None
                    else None
                ),
                "count": rating_stats["count"] or 0,
            },
            "rating_choices": [1, 2, 3, 4, 5],
            "comments": comments,
            "comments_count": comments.count(),
            "page_title": article.title,
            "page_description": article.excerpt or article.title,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Новости", "url": "articles:news_list"},
                {"label": article.title, "url": None},
            ],
        },
    )


def news_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"ok": True, "data": {"results": []}})

    results = (
        _base_published_queryset()
        .filter(
            Q(title__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(content__icontains=q)
            | Q(author__username__icontains=q)
        )
        .order_by("-published_at")[:5]
    )

    return JsonResponse(
        {
            "ok": True,
            "data": {
                "results": [
                    {
                        "title": item.title,
                        "url": item.get_absolute_url(),
                        "published_at": (
                            item.published_at.isoformat() if item.published_at else None
                        ),
                    }
                    for item in results
                ]
            },
        }
    )
