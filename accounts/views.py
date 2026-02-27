from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from comments.models import Comment
from interactions.models import Favorite

from .roles import get_role_label
from .forms import (
    LocalizedPasswordChangeForm,
    LoginForm,
    ProfileEditForm,
    RegisterForm,
)
from .models import Profile

LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 15 * 60


def _safe_redirect_url(request, raw_url):
    if raw_url and url_has_allowed_host_and_scheme(
        url=raw_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return raw_url
    return None


def _resolve_role(user):
    return get_role_label(user)


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "unknown").strip()


def _login_rate_limit_key(request, username):
    normalized = (username or "").strip().lower() or "<empty>"
    return f"login_attempts:{_client_ip(request)}:{normalized}"


def _is_login_rate_limited(request, username):
    attempts = cache.get(_login_rate_limit_key(request, username), 0)
    return attempts >= LOGIN_RATE_LIMIT_MAX_ATTEMPTS


def _bump_login_failures(request, username):
    key = _login_rate_limit_key(request, username)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    return attempts


def _clear_login_failures(request, username):
    cache.delete(_login_rate_limit_key(request, username))


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация выполнена успешно.")
            redirect_to = _safe_redirect_url(request, request.POST.get("next"))
            return redirect(redirect_to or "accounts:profile")
        messages.error(request, "Не удалось зарегистрироваться. Проверьте форму.")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
            "page_title": "Регистрация",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Регистрация", "url": None},
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        redirect_to = _safe_redirect_url(request, request.GET.get("next"))
        return redirect(redirect_to or "accounts:profile")

    next_value = request.GET.get("next", "")
    if request.method == "POST":
        next_value = request.POST.get("next", "")
        username_value = request.POST.get("username", "")
        if _is_login_rate_limited(request, username_value):
            messages.error(
                request,
                "Слишком много неудачных попыток входа. Повторите попытку через 15 минут.",
            )
            form = LoginForm(request, data=request.POST)
            return render(
                request,
                "accounts/login.html",
                {
                    "form": form,
                    "next": next_value,
                    "page_title": "Вход",
                    "breadcrumbs": [
                        {"label": "Главная", "url": "core:home"},
                        {"label": "Вход", "url": None},
                    ],
                },
            )

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            _clear_login_failures(request, username_value)
            messages.success(request, "Вы вошли в аккаунт.")
            redirect_to = _safe_redirect_url(request, next_value)
            return redirect(redirect_to or "accounts:profile")
        _bump_login_failures(request, username_value)
        messages.error(request, "Неверный логин или пароль.")
    else:
        form = LoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_value,
            "page_title": "Вход",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Вход", "url": None},
            ],
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    redirect_to = _safe_redirect_url(request, request.POST.get("next"))
    return redirect(redirect_to or "core:home")


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    recent_favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related("article")
        .order_by("-created_at")[:5]
    )
    recent_comments = (
        Comment.objects.filter(user=request.user)
        .select_related("article")
        .order_by("-created_at")[:5]
    )
    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "role_name": _resolve_role(request.user),
            "recent_favorites": recent_favorites,
            "recent_comments": recent_comments,
            "favorites_count": Favorite.objects.filter(user=request.user).count(),
            "comments_count": Comment.objects.filter(user=request.user).count(),
            "page_title": "Профиль",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Профиль", "url": None},
            ],
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect("accounts:profile")
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "page_title": "Редактирование профиля",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Профиль", "url": "accounts:profile"},
                {"label": "Редактирование", "url": None},
            ],
        },
    )


def password_reset_stub_view(request):
    return render(
        request,
        "accounts/password_reset_stub.html",
        {
            "page_title": "Сброс пароля",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Сброс пароля", "url": None},
            ],
        },
    )


class AccountPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = LocalizedPasswordChangeForm
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Пароль успешно изменен.")
        return super().form_valid(form)
