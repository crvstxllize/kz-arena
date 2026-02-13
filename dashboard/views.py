from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from articles.models import Article

from .decorators import editor_required
from .forms import DashboardArticleForm, MediaAssetForm


def _get_dashboard_articles_queryset(user):
    queryset = Article.objects.select_related("author").prefetch_related("categories", "tags")
    if user.is_staff:
        return queryset
    return queryset.filter(author=user)


def _check_article_permissions(user, article):
    return user.is_staff or article.author_id == user.id


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
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/articles_list.html",
        {
            "page_title": "Управление статьями",
            "page_obj": page_obj,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Статьи", "url": None},
            ],
        },
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
