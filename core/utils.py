from django.utils.text import slugify


def generate_unique_slug(instance, source_value, slug_field="slug", max_length=255):
    base_slug = slugify(source_value)[:max_length] or "item"
    model_class = instance.__class__
    unique_slug = base_slug
    counter = 2

    while (
        model_class.objects.filter(**{slug_field: unique_slug})
        .exclude(pk=instance.pk)
        .exists()
    ):
        suffix = f"-{counter}"
        unique_slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
        counter += 1

    return unique_slug
