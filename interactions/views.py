import json
from functools import wraps

from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from articles.models import Article
from taxonomy.models import Category
from teams.models import Team

from .models import ArticleRating, Favorite, Reaction, Subscription


def _json_error(message, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


def _json_ok(data=None, status=200):
    return JsonResponse({"ok": True, "data": data or {}}, status=status)


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _auth_required_json(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _json_error("Нужно войти", status=401)
        return view_func(request, *args, **kwargs)

    return wrapped


def _reaction_counts(article_id):
    counts = Reaction.objects.filter(article_id=article_id).aggregate(
        likes=Count("id", filter=Q(type=Reaction.TYPE_LIKE)),
        dislikes=Count("id", filter=Q(type=Reaction.TYPE_DISLIKE)),
    )
    return {
        "likes": counts["likes"] or 0,
        "dislikes": counts["dislikes"] or 0,
    }


def _rating_stats(article_id):
    stats = ArticleRating.objects.filter(article_id=article_id).aggregate(
        average=Avg("value"),
        count=Count("id"),
    )
    average = stats["average"]
    return {
        "average": round(float(average), 2) if average is not None else None,
        "count": stats["count"] or 0,
    }


@require_POST
@_auth_required_json
def react_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    article_id = payload.get("article_id")
    reaction_type = payload.get("type")
    if reaction_type not in {Reaction.TYPE_LIKE, Reaction.TYPE_DISLIKE}:
        return _json_error("Недопустимый тип реакции")

    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)

    reaction, created = Reaction.objects.get_or_create(
        article=article,
        user=request.user,
        defaults={"type": reaction_type},
    )

    if not created and reaction.type != reaction_type:
        reaction.type = reaction_type
        reaction.save(update_fields=["type"])

    counts = _reaction_counts(article.pk)
    return _json_ok(
        {
            "article_id": article.pk,
            "reaction": reaction.type,
            "counts": counts,
        }
    )


@require_POST
@_auth_required_json
def favorite_toggle_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    article_id = payload.get("article_id")
    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)

    favorite = Favorite.objects.filter(article=article, user=request.user).first()
    if favorite:
        favorite.delete()
        favorited = False
    else:
        Favorite.objects.create(article=article, user=request.user)
        favorited = True

    total_favorites = Favorite.objects.filter(article=article).count()
    return _json_ok(
        {
            "article_id": article.pk,
            "favorited": favorited,
            "favorites_count": total_favorites,
        }
    )


@require_POST
@_auth_required_json
def subscribe_toggle_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    team_id = payload.get("team_id")
    category_id = payload.get("category_id")

    if not team_id and not category_id:
        return _json_error("Нужно указать team_id или category_id")

    team = get_object_or_404(Team, pk=team_id) if team_id else None
    category = get_object_or_404(Category, pk=category_id) if category_id else None

    sub = Subscription.objects.filter(user=request.user, team=team, category=category).first()
    if sub:
        sub.delete()
        subscribed = False
    else:
        Subscription.objects.create(user=request.user, team=team, category=category)
        subscribed = True

    return _json_ok(
        {
            "subscribed": subscribed,
            "team_id": team.pk if team else None,
            "category_id": category.pk if category else None,
        }
    )


@require_POST
@_auth_required_json
def rate_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    article_id = payload.get("article_id")
    try:
        rating_value = int(payload.get("value"))
    except (TypeError, ValueError):
        return _json_error("Оценка должна быть числом от 1 до 5")

    if rating_value < 1 or rating_value > 5:
        return _json_error("Оценка должна быть в диапазоне 1..5")

    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)
    rating, created = ArticleRating.objects.get_or_create(
        article=article,
        user=request.user,
        defaults={"value": rating_value},
    )
    if not created and rating.value != rating_value:
        rating.value = rating_value
        rating.save(update_fields=["value", "updated_at"])

    return _json_ok(
        {
            "article_id": article.pk,
            "user_rating": rating.value,
            "rating": _rating_stats(article.pk),
        }
    )


@require_GET
@_auth_required_json
def interactions_status_view(request):
    article_id = request.GET.get("article_id")
    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)

    reaction = Reaction.objects.filter(article=article, user=request.user).first()
    favorited = Favorite.objects.filter(article=article, user=request.user).exists()
    user_rating = (
        ArticleRating.objects.filter(article=article, user=request.user)
        .values_list("value", flat=True)
        .first()
    )

    counts = _reaction_counts(article.pk)
    rating = _rating_stats(article.pk)

    return _json_ok(
        {
            "article_id": article.pk,
            "liked": reaction.type == Reaction.TYPE_LIKE if reaction else False,
            "disliked": reaction.type == Reaction.TYPE_DISLIKE if reaction else False,
            "favorited": favorited,
            "counts": counts,
            "user_rating": user_rating,
            "rating": rating,
        }
    )
