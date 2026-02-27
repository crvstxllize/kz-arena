from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt

from articles.models import Article
from taxonomy.models import Category, Tag
from teams.models import Team
from tournaments.models import Tournament

from .decorators import is_editor_or_staff, require_role_editor
from .utils import json_error, json_ok, parse_json_body


def _method_not_allowed():
    return json_error(
        code="method_not_allowed",
        message="Метод не поддерживается для этого endpoint.",
        status=405,
    )


def _file_url(request, field):
    if not field:
        return None

    try:
        return request.build_absolute_uri(field.url)
    except ValueError:
        return None


def _serialize_article(article, request):
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "excerpt": article.excerpt,
        "kind": article.kind,
        "discipline": article.discipline,
        "status": article.status,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "views_count": article.views_count,
        "author": {"username": article.author.username},
        "categories": [{"name": c.name, "slug": c.slug} for c in article.categories.all()],
        "tags": [{"name": t.name, "slug": t.slug} for t in article.tags.all()],
        "cover_url": _file_url(request, article.cover),
    }


def _validate_article_payload(payload, partial=False):
    errors = {}

    valid_kinds = {choice[0] for choice in Article.CONTENT_KIND_CHOICES}
    valid_disciplines = {choice[0] for choice in Article.DISCIPLINE_CHOICES}
    valid_statuses = {choice[0] for choice in Article.STATUS_CHOICES}

    if not partial or "title" in payload:
        if not str(payload.get("title") or "").strip():
            errors["title"] = "Поле title обязательно."

    if not partial or "content" in payload:
        if not str(payload.get("content") or "").strip():
            errors["content"] = "Поле content обязательно."

    if not partial or "kind" in payload:
        if payload.get("kind") not in valid_kinds:
            errors["kind"] = "Недопустимое значение kind."

    if "discipline" in payload and payload.get("discipline"):
        if payload["discipline"] not in valid_disciplines:
            errors["discipline"] = "Недопустимое значение discipline."

    if "status" in payload and payload.get("status") not in valid_statuses:
        errors["status"] = "Недопустимое значение status."

    if "category_slugs" in payload and not isinstance(payload.get("category_slugs"), list):
        errors["category_slugs"] = "Поле category_slugs должно быть списком."

    if "tag_slugs" in payload and not isinstance(payload.get("tag_slugs"), list):
        errors["tag_slugs"] = "Поле tag_slugs должно быть списком."

    return errors


def _resolve_taxonomy(payload):
    details = {}
    categories = None
    tags = None

    if "category_slugs" in payload:
        category_slugs = [
            str(slug).strip() for slug in payload.get("category_slugs", []) if str(slug).strip()
        ]
        categories = list(Category.objects.filter(slug__in=category_slugs))
        found = {c.slug for c in categories}
        missing = [slug for slug in category_slugs if slug not in found]
        if missing:
            details["missing_category_slugs"] = missing

    if "tag_slugs" in payload:
        tag_slugs = [
            str(slug).strip() for slug in payload.get("tag_slugs", []) if str(slug).strip()
        ]
        tags = list(Tag.objects.filter(slug__in=tag_slugs))
        found = {t.slug for t in tags}
        missing = [slug for slug in tag_slugs if slug not in found]
        if missing:
            details["missing_tag_slugs"] = missing

    return categories, tags, details


@csrf_exempt
def articles_collection(request):
    if request.method == "GET":
        queryset = (
            Article.objects.filter(status=Article.STATUS_PUBLISHED)
            .select_related("author")
            .prefetch_related("categories", "tags")
        )

        q = request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content__icontains=q)
                | Q(author__username__icontains=q)
            )

        category_slug = request.GET.get("category", "").strip()
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)

        tag_slug = request.GET.get("tag", "").strip()
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        kind = request.GET.get("kind", "").strip()
        valid_kinds = {choice[0] for choice in Article.CONTENT_KIND_CHOICES}
        if kind in valid_kinds:
            queryset = queryset.filter(kind=kind)

        discipline = request.GET.get("discipline", "").strip()
        valid_disciplines = {choice[0] for choice in Article.DISCIPLINE_CHOICES}
        if discipline in valid_disciplines:
            queryset = queryset.filter(discipline=discipline)

        ordering = request.GET.get("ordering", "new").strip()
        if ordering == "popular":
            queryset = queryset.order_by("-views_count", "-published_at")
        else:
            ordering = "new"
            queryset = queryset.order_by("-published_at", "-id")

        queryset = queryset.distinct()

        try:
            page = int(request.GET.get("page", "1"))
            page_size = int(request.GET.get("page_size", "10"))
        except ValueError:
            return json_error(
                code="validation_error",
                message="Параметры page и page_size должны быть числами.",
                status=400,
            )

        page = max(page, 1)
        page_size = max(1, min(page_size, 50))

        total = queryset.count()
        pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size

        items = [_serialize_article(article, request) for article in queryset[start:end]]

        return json_ok(
            {
                "items": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "pages": pages,
                },
            }
        )

    if request.method != "POST":
        return _method_not_allowed()

    if not is_editor_or_staff(request.user):
        return json_error(
            code="forbidden",
            message="Недостаточно прав для создания статьи.",
            status=403,
        )

    payload, error_response = parse_json_body(request)
    if error_response:
        return error_response

    field_errors = _validate_article_payload(payload, partial=False)
    if field_errors:
        return json_error(
            code="validation_error",
            message="Ошибка валидации полей.",
            status=400,
            details=field_errors,
        )

    categories, tags, taxonomy_errors = _resolve_taxonomy(payload)
    if taxonomy_errors:
        return json_error(
            code="validation_error",
            message="Некоторые категории или теги не найдены.",
            status=400,
            details=taxonomy_errors,
        )

    article = Article(
        title=str(payload.get("title") or "").strip(),
        excerpt=str(payload.get("excerpt") or "").strip(),
        content=str(payload.get("content") or "").strip(),
        kind=payload.get("kind"),
        discipline=str(payload.get("discipline") or "").strip(),
        status=payload.get("status") or Article.STATUS_DRAFT,
        is_featured=bool(payload.get("is_featured", False)),
        author=request.user,
    )
    article.save()

    if categories is not None:
        article.categories.set(categories)
    if tags is not None:
        article.tags.set(tags)

    article = (
        Article.objects.select_related("author")
        .prefetch_related("categories", "tags")
        .get(pk=article.pk)
    )

    return json_ok(_serialize_article(article, request), status=201)


def article_detail(request, slug):
    if request.method != "GET":
        return _method_not_allowed()

    article = (
        Article.objects.filter(status=Article.STATUS_PUBLISHED, slug=slug)
        .select_related("author")
        .prefetch_related("categories", "tags", "assets")
        .first()
    )
    if not article:
        return json_error(
            code="not_found",
            message="Статья не найдена.",
            status=404,
        )

    data = _serialize_article(article, request)
    data["content"] = article.content
    data["assets"] = [
        {
            "file_url": _file_url(request, asset.file),
            "caption": asset.caption,
        }
        for asset in article.assets.all()
    ]

    return json_ok(data)


@csrf_exempt
@require_role_editor
def article_by_pk(request, pk):
    if request.method not in {"PUT", "DELETE"}:
        return _method_not_allowed()

    article = (
        Article.objects.select_related("author")
        .prefetch_related("categories", "tags")
        .filter(pk=pk)
        .first()
    )
    if not article:
        return json_error(
            code="not_found",
            message="Статья не найдена.",
            status=404,
        )

    if not (request.user.is_staff or article.author_id == request.user.id):
        return json_error(
            code="forbidden",
            message="Недостаточно прав для изменения статьи.",
            status=403,
        )

    if request.method == "DELETE":
        article.delete()
        return json_ok({"deleted": True})

    payload, error_response = parse_json_body(request)
    if error_response:
        return error_response

    field_errors = _validate_article_payload(payload, partial=True)
    if field_errors:
        return json_error(
            code="validation_error",
            message="Ошибка валидации полей.",
            status=400,
            details=field_errors,
        )

    categories, tags, taxonomy_errors = _resolve_taxonomy(payload)
    if taxonomy_errors:
        return json_error(
            code="validation_error",
            message="Некоторые категории или теги не найдены.",
            status=400,
            details=taxonomy_errors,
        )

    editable_fields = ["title", "excerpt", "content", "kind", "discipline", "status", "is_featured"]
    for field in editable_fields:
        if field not in payload:
            continue

        value = payload[field]
        if field in {"title", "excerpt", "content", "discipline"}:
            value = str(value or "").strip()
        if field == "is_featured":
            value = bool(value)
        setattr(article, field, value)

    article.save()

    if categories is not None:
        article.categories.set(categories)
    if tags is not None:
        article.tags.set(tags)

    article = (
        Article.objects.select_related("author")
        .prefetch_related("categories", "tags")
        .get(pk=article.pk)
    )

    return json_ok(_serialize_article(article, request))


def teams_list(request):
    if request.method != "GET":
        return _method_not_allowed()

    queryset = Team.objects.annotate(players_count=Count("players"))

    kind = request.GET.get("kind", "").strip()
    valid_kinds = {choice[0] for choice in Team.CONTENT_KIND_CHOICES}
    if kind in valid_kinds:
        queryset = queryset.filter(kind=kind)

    discipline = request.GET.get("discipline", "").strip()
    valid_disciplines = {choice[0] for choice in Team.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    items = [
        {
            "id": team.id,
            "name": team.name,
            "slug": team.slug,
            "kind": team.kind,
            "discipline": team.discipline,
            "country": team.country,
            "logo_url": _file_url(request, team.logo),
            "players_count": team.players_count,
        }
        for team in queryset.order_by("name")
    ]

    return json_ok({"items": items})


def tournaments_list(request):
    if request.method != "GET":
        return _method_not_allowed()

    queryset = Tournament.objects.annotate(matches_count=Count("matches"))

    kind = request.GET.get("kind", "").strip()
    valid_kinds = {choice[0] for choice in Tournament.CONTENT_KIND_CHOICES}
    if kind in valid_kinds:
        queryset = queryset.filter(kind=kind)

    discipline = request.GET.get("discipline", "").strip()
    valid_disciplines = {choice[0] for choice in Tournament.DISCIPLINE_CHOICES}
    if discipline in valid_disciplines:
        queryset = queryset.filter(discipline=discipline)

    items = [
        {
            "id": tournament.id,
            "name": tournament.name,
            "slug": tournament.slug,
            "kind": tournament.kind,
            "discipline": tournament.discipline,
            "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
            "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
            "location": tournament.location,
            "matches_count": tournament.matches_count,
        }
        for tournament in queryset.order_by("-start_date")
    ]

    return json_ok({"items": items})


def global_search(request):
    if request.method != "GET":
        return _method_not_allowed()

    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return json_error(
            code="validation_error",
            message="Параметр q обязателен и должен содержать минимум 2 символа.",
            status=400,
        )

    articles = (
        Article.objects.filter(status=Article.STATUS_PUBLISHED)
        .filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))
        .order_by("-published_at")[:5]
    )
    teams = Team.objects.filter(name__icontains=q).order_by("name")[:5]
    tournaments = Tournament.objects.filter(name__icontains=q).order_by("-start_date")[:5]

    return json_ok(
        {
            "articles": [{"title": article.title, "slug": article.slug} for article in articles],
            "teams": [{"name": team.name, "slug": team.slug} for team in teams],
            "tournaments": [
                {"name": tournament.name, "slug": tournament.slug} for tournament in tournaments
            ],
        }
    )


def api_root(request):
    if request.method != "GET":
        return _method_not_allowed()

    return json_ok(
        {
            "endpoints": {
                "articles": "/api/articles/",
                "article_detail": "/api/articles/<slug:slug>/",
                "teams": "/api/teams/",
                "tournaments": "/api/tournaments/",
                "search": "/api/search/",
            }
        }
    )
