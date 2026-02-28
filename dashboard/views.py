from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile
from accounts.roles import (
    can_edit_articles,
    can_manage_users,
    get_role_key,
    get_role_label,
    set_user_role,
)
from articles.models import Article
from comments.models import Comment, CommentReport
from interactions.models import ArticleRating, Favorite, Reaction, Subscription
from teams.models import Team

from .decorators import editor_required, staff_required
from .forms import DashboardArticleForm, MediaAssetForm, TeamDashboardForm, TeamMemberFormSet

DELETED_USERNAME = "deleted_user"
DELETED_DISPLAY_NAME = "Удалённый пользователь"
ROLE_CHOICES = (
    ("user", "Пользователь"),
    ("editor", "Редактор"),
    ("admin", "Администратор"),
)


def _get_dashboard_articles_queryset(user):
    queryset = Article.objects.select_related("author").prefetch_related("categories", "tags")
    if can_edit_articles(user):
        return queryset
    return queryset.filter(author=user)


def _check_article_permissions(user, article):
    return can_edit_articles(user) or article.author_id == user.id


def _get_dashboard_teams_queryset():
    return Team.objects.filter(is_manual=True).prefetch_related("players")


def _get_moderatable_users_queryset():
    return (
        User.objects.exclude(is_superuser=True)
        .exclude(username=DELETED_USERNAME)
        .select_related("profile")
        .order_by("username")
        .distinct()
    )


def _get_or_create_deleted_user():
    deleted_user, created = User.objects.get_or_create(
        username=DELETED_USERNAME,
        defaults={
            "email": "",
            "first_name": "Deleted",
            "last_name": "User",
            "is_active": False,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    if created:
        deleted_user.set_unusable_password()
        deleted_user.save(update_fields=["password"])

    changed_fields = []
    if deleted_user.is_active:
        deleted_user.is_active = False
        changed_fields.append("is_active")
    if deleted_user.is_staff:
        deleted_user.is_staff = False
        changed_fields.append("is_staff")
    if deleted_user.is_superuser:
        deleted_user.is_superuser = False
        changed_fields.append("is_superuser")
    if changed_fields:
        deleted_user.save(update_fields=changed_fields)

    deleted_user.groups.clear()
    profile, _ = Profile.objects.get_or_create(user=deleted_user)
    if profile.display_name != DELETED_DISPLAY_NAME:
        profile.display_name = DELETED_DISPLAY_NAME
        profile.save(update_fields=["display_name"])

    return deleted_user


def _delete_user_safely(target_user):
    with transaction.atomic():
        deleted_user = _get_or_create_deleted_user()
        if target_user.pk == deleted_user.pk:
            raise ValueError("Системного пользователя deleted_user удалять нельзя.")

        Article.objects.filter(author=target_user).update(author=deleted_user)
        Comment.objects.filter(user=target_user).update(user=deleted_user)
        CommentReport.objects.filter(user=target_user).update(user=deleted_user)

        # These models have unique constraints by (entity, user), so we remove them.
        Reaction.objects.filter(user=target_user).delete()
        Favorite.objects.filter(user=target_user).delete()
        Subscription.objects.filter(user=target_user).delete()
        ArticleRating.objects.filter(user=target_user).delete()

        target_user.groups.clear()
        target_user.delete()


@login_required
@editor_required
def dashboard_index(request):
    articles_qs = _get_dashboard_articles_queryset(request.user)
    teams_qs = _get_dashboard_teams_queryset()
    return render(
        request,
        "dashboard/index.html",
        {
            "page_title": "Dashboard",
            "total_articles": articles_qs.count(),
            "published_articles": articles_qs.filter(status=Article.STATUS_PUBLISHED).count(),
            "draft_articles": articles_qs.filter(status=Article.STATUS_DRAFT).count(),
            "total_teams": teams_qs.count(),
            "can_manage_users": can_manage_users(request.user),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": None},
            ],
        },
    )


@login_required
@editor_required
def article_list(request):
    queryset = _get_dashboard_articles_queryset(request.user).order_by("-created_at", "-id")
    query = (request.GET.get("q") or request.GET.get("slug") or "").strip()
    if query:
        queryset = queryset.filter(Q(slug__icontains=query) | Q(title__icontains=query))
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/articles_list.html",
        {
            "page_title": "Управление статьями",
            "page_obj": page_obj,
            "query": query,
            "search_url": reverse("dashboard:article_search"),
            "reset_url": reverse("dashboard:article_list"),
            "can_manage_users": can_manage_users(request.user),
            "can_manage_teams": can_edit_articles(request.user),
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
        .order_by("-created_at", "-id")[:5]
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
            if article.is_featured:
                Article.objects.filter(is_featured=True).exclude(pk=article.pk).update(
                    is_featured=False
                )
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
            updated_article = form.save()
            if updated_article.is_featured:
                Article.objects.filter(is_featured=True).exclude(pk=updated_article.pk).update(
                    is_featured=False
                )
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
        article.published_at = timezone.now()
        message_text = "Статья опубликована."
    else:
        article.status = Article.STATUS_DRAFT
        message_text = "Статья снята с публикации."

    article.save(update_fields=["status", "published_at", "updated_at"])
    messages.success(request, message_text)
    return redirect("dashboard:article_list")


@login_required
@editor_required
def team_list(request):
    queryset = _get_dashboard_teams_queryset().order_by("name", "id")
    query = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "").strip()
    discipline = request.GET.get("discipline", "").strip()

    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(slug__icontains=query)
            | Q(city__icontains=query)
            | Q(country__icontains=query)
            | Q(description__icontains=query)
        )
    if kind in {Team.KIND_SPORT, Team.KIND_ESPORT}:
        queryset = queryset.filter(kind=kind)
    if discipline in {value for value, _ in Team.DISCIPLINE_CHOICES}:
        queryset = queryset.filter(discipline=discipline)

    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "dashboard/teams_list.html",
        {
            "page_title": "Управление командами",
            "page_obj": page_obj,
            "query": query,
            "current_filters": {
                "kind": kind,
                "discipline": discipline,
            },
            "kind_choices": Team.CONTENT_KIND_CHOICES,
            "discipline_choices": Team.DISCIPLINE_CHOICES,
            "pagination_query": query_params.urlencode(),
            "reset_url": reverse("dashboard:team_list"),
            "can_manage_users": can_manage_users(request.user),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Команды", "url": None},
            ],
        },
    )


@login_required
@editor_required
def team_create(request):
    if request.method == "POST":
        form = TeamDashboardForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            team.is_manual = True
            team.save()
            messages.success(request, "Команда создана. Добавьте состав в форме редактирования.")
            return redirect("dashboard:team_edit", pk=team.pk)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = TeamDashboardForm()

    return render(
        request,
        "dashboard/team_form.html",
        {
            "page_title": "Создать команду",
            "team": None,
            "form": form,
            "members_formset": None,
            "can_manage_users": can_manage_users(request.user),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Команды", "url": "dashboard:team_list"},
                {"label": "Создать", "url": None},
            ],
        },
    )


@login_required
@editor_required
def team_edit(request, pk):
    team = get_object_or_404(_get_dashboard_teams_queryset(), pk=pk)

    if request.method == "POST":
        form = TeamDashboardForm(request.POST, request.FILES, instance=team)
        members_formset = TeamMemberFormSet(
            request.POST,
            request.FILES,
            instance=team,
            prefix="members",
        )
        if form.is_valid() and members_formset.is_valid():
            with transaction.atomic():
                updated_team = form.save(commit=False)
                updated_team.is_manual = True
                updated_team.save()
                members_formset.save()
            messages.success(request, "Изменения команды и состава сохранены.")
            return redirect("dashboard:team_edit", pk=team.pk)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = TeamDashboardForm(instance=team)
        members_formset = TeamMemberFormSet(instance=team, prefix="members")

    return render(
        request,
        "dashboard/team_form.html",
        {
            "page_title": f"Команда: {team.name}",
            "team": team,
            "form": form,
            "members_formset": members_formset,
            "can_manage_users": can_manage_users(request.user),
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Команды", "url": "dashboard:team_list"},
                {"label": "Редактирование", "url": None},
            ],
        },
    )


@login_required
@editor_required
def team_delete(request, pk):
    team = get_object_or_404(_get_dashboard_teams_queryset(), pk=pk)
    if request.method == "POST":
        try:
            team.delete()
            messages.success(request, "Команда удалена.")
        except ProtectedError:
            messages.error(
                request,
                "Команду нельзя удалить: она связана с матчами/турнирами. Сначала измените связанные данные.",
            )
        return redirect("dashboard:team_list")

    return render(
        request,
        "dashboard/team_confirm_delete.html",
        {
            "page_title": "Удаление команды",
            "team": team,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Dashboard", "url": "dashboard:index"},
                {"label": "Команды", "url": "dashboard:team_list"},
                {"label": "Удаление", "url": None},
            ],
        },
    )


@login_required
@staff_required
def user_list(request):
    base_queryset = _get_moderatable_users_queryset()
    query = request.GET.get("q", "").strip()

    filtered_queryset = base_queryset
    if query:
        filtered_queryset = filtered_queryset.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(profile__display_name__icontains=query)
        )

    paginator = Paginator(filtered_queryset.distinct(), 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    for user_item in page_obj.object_list:
        user_item.role_key = get_role_key(user_item)
        user_item.role_label = get_role_label(user_item)

    return render(
        request,
        "dashboard/users_list.html",
        {
            "page_title": "Модерация пользователей",
            "page_obj": page_obj,
            "query": query,
            "reset_url": reverse("dashboard:user_list"),
            "active_count": base_queryset.filter(is_active=True).count(),
            "banned_count": base_queryset.filter(is_active=False).count(),
            "total_users_count": base_queryset.count(),
            "role_choices": ROLE_CHOICES,
            "can_manage_teams": can_edit_articles(request.user),
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
    if target_user.pk == request.user.pk:
        messages.error(request, "Нельзя забанить или разбанить самого себя.")
        return redirect("dashboard:user_list")

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])

    if target_user.is_active:
        messages.success(request, f"Пользователь {target_user.username} разбанен.")
    else:
        messages.success(request, f"Пользователь {target_user.username} забанен.")

    return redirect("dashboard:user_list")


@login_required
@staff_required
@require_POST
def user_set_role(request, pk):
    target_user = get_object_or_404(_get_moderatable_users_queryset(), pk=pk)
    if target_user.pk == request.user.pk:
        messages.error(request, "Нельзя менять роль самому себе.")
        return redirect("dashboard:user_list")

    role = (request.POST.get("role") or "").strip()
    if role not in {item[0] for item in ROLE_CHOICES}:
        messages.error(request, "Неизвестная роль.")
        return redirect("dashboard:user_list")

    old_role = get_role_label(target_user)
    set_user_role(target_user, role)
    messages.success(request, f"Роль пользователя {target_user.username}: {old_role} -> {get_role_label(target_user)}.")
    return redirect("dashboard:user_list")


@login_required
@staff_required
@require_POST
def user_delete(request, pk):
    target_user = get_object_or_404(_get_moderatable_users_queryset(), pk=pk)
    if target_user.pk == request.user.pk:
        messages.error(request, "Нельзя удалить самого себя.")
        return redirect("dashboard:user_list")

    try:
        username = target_user.username
        _delete_user_safely(target_user)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("dashboard:user_list")

    messages.success(request, f"Пользователь {username} удален. Связанные данные обработаны безопасно.")
    return redirect("dashboard:user_list")
