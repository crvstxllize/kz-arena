from django import template
from django.templatetags.static import static

from teams.assets import resolve_team_logo_asset

register = template.Library()


@register.filter(name="team_logo_url")
def team_logo_url(team):
    logo = getattr(team, "logo", None)
    if logo and getattr(logo, "name", ""):
        try:
            if logo.storage.exists(logo.name):
                return logo.url
        except Exception:
            pass

    mapped = resolve_team_logo_asset(getattr(team, "name", ""))
    if mapped:
        return static(mapped)
    return static("img/placeholder.svg")
