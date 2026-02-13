from functools import wraps

from .utils import json_error


def is_editor_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name="Editors").exists())


def require_role_editor(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_editor_or_staff(request.user):
            return json_error(
                code="forbidden",
                message="Недостаточно прав для выполнения действия.",
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return wrapped
