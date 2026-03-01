from django import template
from django.templatetags.static import static

from core.data.news import NEWS_ITEMS

register = template.Library()

PLACEHOLDER_BY_DISCIPLINE = {
    "football": "placeholders/news/football.svg",
    "basketball": "placeholders/news/basketball.svg",
    "athletics": "placeholders/news/default.svg",
    "cs2": "placeholders/news/cs2.svg",
    "dota2": "placeholders/news/dota2.svg",
    "pubg": "placeholders/news/pubg.svg",
}

KEYWORD_MAP = {
    "football": "football",
    "футбол": "football",
    "basketball": "basketball",
    "баскетбол": "basketball",
    "athletics": "athletics",
    "легкая атлетика": "athletics",
    "лёгкая атлетика": "athletics",
    "марафон": "athletics",
    "бег": "athletics",
    "cs2": "cs2",
    "counter-strike": "cs2",
    "dota2": "dota2",
    "dota 2": "dota2",
    "pubg": "pubg",
}

NEWS_IMAGE_BY_TITLE = {
    str(item.get("title") or "").strip().lower(): item.get("image")
    for item in NEWS_ITEMS
    if item.get("title") and item.get("image")
}


def _has_cover_file(article):
    cover = getattr(article, "cover", None)
    if not cover:
        return False
    name = getattr(cover, "name", "")
    if not name:
        return False
    storage = getattr(cover, "storage", None)
    if not storage:
        return False
    try:
        return storage.exists(name)
    except Exception:
        return False


def _resolve_discipline(article):
    discipline = (getattr(article, "discipline", "") or "").strip().lower()
    if discipline in PLACEHOLDER_BY_DISCIPLINE:
        return discipline

    parts = [getattr(article, "title", "") or "", getattr(article, "excerpt", "") or ""]
    categories = getattr(article, "categories", None)
    if categories is not None:
        try:
            parts.extend(categories.values_list("name", flat=True))
        except Exception:
            pass
    tags = getattr(article, "tags", None)
    if tags is not None:
        try:
            parts.extend(tags.values_list("name", flat=True))
        except Exception:
            pass

    haystack = " ".join(str(part).lower() for part in parts if part)
    for keyword, mapped in KEYWORD_MAP.items():
        if keyword in haystack:
            return mapped
    return "default"


def _resolve_placeholder_path(article):
    discipline = _resolve_discipline(article)
    return PLACEHOLDER_BY_DISCIPLINE.get(discipline, "placeholders/news/default.svg")


def _resolve_seed_image(article):
    title = str(getattr(article, "title", "") or "").strip().lower()
    return NEWS_IMAGE_BY_TITLE.get(title)


@register.filter(name="news_image")
def news_image(article):
    if _has_cover_file(article):
        return article.cover.url
    seed_url = _resolve_seed_image(article)
    if seed_url:
        return seed_url
    return static(_resolve_placeholder_path(article))


@register.filter(name="news_placeholder")
def news_placeholder(article):
    return static(_resolve_placeholder_path(article))
