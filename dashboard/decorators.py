from functools import wraps

from django.core.exceptions import PermissionDenied

from accounts.roles import can_edit_articles, can_manage_users


def editor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if can_edit_articles(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("У вас нет доступа к dashboard.")

    return _wrapped_view


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if can_manage_users(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Доступ только для администратора.")

    return _wrapped_view
