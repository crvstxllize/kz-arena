from django import template

from core.utils import get_public_name

register = template.Library()


@register.filter
def public_name(user):
    return get_public_name(user)
