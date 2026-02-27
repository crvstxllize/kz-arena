from functools import wraps

from django.core.exceptions import PermissionDenied


def editor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.groups.filter(name="Editors").exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("У вас нет доступа к dashboard.")

    return _wrapped_view


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Доступ только для администратора.")

    return _wrapped_view
