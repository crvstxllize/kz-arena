import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from articles.models import Article
from core.utils import get_public_name

from .models import Comment


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


@require_POST
@_auth_required_json
def comment_add_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    article_id = payload.get("article_id")
    text = (payload.get("text") or "").strip()

    if not text:
        return _json_error("Комментарий не может быть пустым")
    if len(text) > 2000:
        return _json_error("Комментарий слишком длинный")

    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)
    comment = Comment.objects.create(
        article=article,
        user=request.user,
        text=text,
        is_approved=True,
    )

    html = render_to_string(
        "comments/comment_item.html",
        {
            "comment": comment,
            "user": request.user,
        },
        request=request,
    )

    return _json_ok(
        {
            "comment": {
                "id": comment.pk,
                "text": comment.text,
                "username": get_public_name(comment.user),
                "login": comment.user.username,
                "created_at": comment.created_at.isoformat(),
            },
            "html": html,
        }
    )


@require_POST
@_auth_required_json
def comment_delete_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Некорректный JSON")

    comment_id = payload.get("comment_id")
    comment = get_object_or_404(Comment, pk=comment_id)

    if not (request.user.is_staff or comment.user_id == request.user.id):
        return _json_error("Недостаточно прав", status=403)

    comment.delete()
    return _json_ok({"comment_id": comment_id})


@require_GET
def comment_list_view(request):
    article_id = request.GET.get("article_id")
    article = get_object_or_404(Article, pk=article_id, status=Article.STATUS_PUBLISHED)

    comments = (
        Comment.objects.filter(article=article, is_approved=True)
        .select_related("user", "user__profile")
    )
    html = render_to_string(
        "comments/comment_list_items.html",
        {
            "comments": comments,
            "user": request.user,
        },
        request=request,
    )

    return _json_ok(
        {
            "count": comments.count(),
            "html": html,
        }
    )
