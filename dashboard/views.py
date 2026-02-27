from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from articles.models import Article

from .decorators import editor_required, staff_required
from .forms import DashboardArticleForm, MediaAssetForm


def _get_dashboard_articles_queryset(user):
    queryset = Article.objects.select_related("author").prefetch_related("categories", "tags")
    if user.is_staff:
        return queryset
    return queryset.filter(author=user)


def _check_article_permissions(user, article):
    return user.is_staff or article.author_id == user.id


def _get_moderatable_users_queryset():
    return (
        User.objects.exclude(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name="Editors"))
        .order_by("username")
        .distinct()
    )


@login_required
@editor_required
def dashboard_index(request):
    articles_qs = _get_dashboard_articles_queryset(request.user)
    return render(
        request,
        "dashboard/index.html",
        {
            "page_title": "Dashboard",
            "total_articles": articles_qs.count(),
            "published_articles": articles_qs.filter(status=Article.STATUS_PUBLISHED).count(),
            "draft_articles": articles_qs.filter(status=Article.STATUS_DRAFT).count(),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": None},
            ],
        },
    )


@login_required
@editor_required
def article_list(request):
    queryset = _get_dashboard_articles_queryset(request.user).order_by("-updated_at")
    slug_query = request.GET.get("slug", "").strip()
    if slug_query:
        queryset = queryset.filter(Q(slug__icontains=slug_query) | Q(title__icontains=slug_query))
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/articles_list.html",
        {
            "page_title": "Управление статьями",
            "page_obj": page_obj,
            "slug_query": slug_query,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Статьи", "url": None},
            ],
        },
    )


@login_required
@editor_required
def article_search(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"ok": True, "data": {"results": []}})

    items = (
        _get_dashboard_articles_queryset(request.user)
        .filter(Q(title__icontains=q) | Q(slug__icontains=q))
        .order_by("-updated_at")[:5]
    )

    return JsonResponse(
        {
            "ok": True,
            "data": {
                "results": [
                    {
                        "title": f"{article.title} ({article.slug})",
                        "url": reverse("dashboard:article_edit", args=[article.pk]),
                    }
                    for article in items
                ]
            },
        }
    )


@login_required
@editor_required
def article_create(request):
    if request.method == "POST":
        form = DashboardArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = Article.STATUS_DRAFT
            article.save()
            form.save_m2m()
            messages.success(request, "Статья создана в статусе черновика.")
            return redirect("dashboard:article_edit", pk=article.pk)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = DashboardArticleForm()

    return render(
        request,
        "dashboard/article_form.html",
        {
            "page_title": "Создать статью",
            "form": form,
            "article": None,
            "asset_form": None,
            "asset_items": [],
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Создать статью", "url": None},
            ],
        },
    )


@login_required
@editor_required
def article_edit(request, pk):
    article = get_object_or_404(Article.objects.prefetch_related("assets"), pk=pk)

    if not _check_article_permissions(request.user, article):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("У вас нет доступа к этой статье.")

    if request.method == "POST" and "add_asset" in request.POST:
        asset_form = MediaAssetForm(request.POST, request.FILES)
        form = DashboardArticleForm(instance=article)
        if asset_form.is_valid():
            asset = asset_form.save(commit=False)
            asset.article = article
            asset.save()
            messages.success(request, "Дополнительное изображение добавлено.")
            return redirect("dashboard:article_edit", pk=article.pk)
        messages.error(request, "Не удалось добавить изображение.")
    elif request.method == "POST":
        form = DashboardArticleForm(request.POST, request.FILES, instance=article)
        asset_form = MediaAssetForm()
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("dashboard:article_edit", pk=article.pk)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = DashboardArticleForm(instance=article)
        asset_form = MediaAssetForm()

    return render(
        request,
        "dashboard/article_form.html",
        {
            "page_title": f"Редактирование: {article.title}",
            "form": form,
            "article": article,
            "asset_form": asset_form,
            "asset_items": article.assets.all(),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Статьи", "url": "dashboard:article_list"},
                {"label": "Редактирование", "url": None},
            ],
        },
    )


@login_required
@editor_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if not _check_article_permissions(request.user, article):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("У вас нет доступа к этой статье.")

    if request.method == "POST":
        article.delete()
        messages.success(request, "Статья удалена.")
        return redirect("dashboard:article_list")

    return render(
        request,
        "dashboard/article_confirm_delete.html",
        {
            "page_title": "Удаление статьи",
            "article": article,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Статьи", "url": "dashboard:article_list"},
                {"label": "Удаление", "url": None},
            ],
        },
    )


@login_required
@editor_required
@require_POST
def article_bulk_delete(request):
    raw_ids = request.POST.getlist("article_ids")
    article_ids = []
    for raw_id in raw_ids:
        try:
            article_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    unique_ids = sorted(set(article_ids))
    if not unique_ids:
        messages.warning(request, "Выберите хотя бы одну статью.")
        return redirect("dashboard:article_list")

    queryset = _get_dashboard_articles_queryset(request.user).filter(pk__in=unique_ids)
    deleted_articles_count = queryset.count()

    if not deleted_articles_count:
        messages.warning(request, "Нет доступных статей для удаления.")
        return redirect("dashboard:article_list")

    queryset.delete()

    skipped_count = len(unique_ids) - deleted_articles_count
    messages.success(request, f"Удалено статей: {deleted_articles_count}.")
    if skipped_count > 0:
        messages.warning(
            request,
            f"Пропущено статей (нет доступа или не найдены): {skipped_count}.",
        )
    return redirect("dashboard:article_list")


@login_required
@editor_required
@require_POST
def article_toggle_status(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if not _check_article_permissions(request.user, article):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("У вас нет доступа к этой статье.")

    if article.status == Article.STATUS_DRAFT:
        article.status = Article.STATUS_PUBLISHED
        if not article.published_at:
            article.published_at = timezone.now()
        message_text = "Статья опубликована."
    else:
        article.status = Article.STATUS_DRAFT
        message_text = "Статья снята с публикации."

    article.save(update_fields=["status", "published_at", "updated_at"])
    messages.success(request, message_text)
    return redirect("dashboard:article_list")


@login_required
@staff_required
def user_list(request):
    queryset = _get_moderatable_users_queryset()
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/users_list.html",
        {
            "page_title": "Модерация пользователей",
            "page_obj": page_obj,
            "active_count": queryset.filter(is_active=True).count(),
            "banned_count": queryset.filter(is_active=False).count(),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Пользователи", "url": None},
            ],
        },
    )


@login_required
@staff_required
@require_POST
def user_toggle_ban(request, pk):
    target_user = get_object_or_404(_get_moderatable_users_queryset(), pk=pk)
    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])

    if target_user.is_active:
        messages.success(request, f"Пользователь {target_user.username} разбанен.")
    else:
        messages.success(request, f"Пользователь {target_user.username} забанен.")

    return redirect("dashboard:user_list")
