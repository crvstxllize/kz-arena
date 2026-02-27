from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify


def _normalized_text(value):
    if value is None:
        return ""
    return str(value).strip()


def get_public_name(user):
    if not user:
        return "Пользователь"

    direct_display_name = _normalized_text(getattr(user, "display_name", ""))
    if direct_display_name:
        return direct_display_name

    profile_display_name = ""
    try:
        profile = user.profile
    except (AttributeError, ObjectDoesNotExist):
        profile = None
    if profile is not None:
        profile_display_name = _normalized_text(getattr(profile, "display_name", ""))
    if profile_display_name:
        return profile_display_name

    full_name = _normalized_text(user.get_full_name() if hasattr(user, "get_full_name") else "")
    if full_name:
        return full_name

    first_name = _normalized_text(getattr(user, "first_name", ""))
    if first_name:
        return first_name

    username = _normalized_text(getattr(user, "username", ""))
    if username:
        return username

    return "Пользователь"


def generate_unique_slug(instance, source_value, slug_field="slug", max_length=255):
    base_slug = slugify(source_value, allow_unicode=True)[:max_length] or "item"
    model_class = instance.__class__
    unique_slug = base_slug
    counter = 2

    while model_class.objects.filter(**{slug_field: unique_slug}).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        unique_slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
        counter += 1

    return unique_slug
