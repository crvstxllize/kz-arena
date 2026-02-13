from django.contrib import admin
from django.utils import timezone

from .models import Article, MediaAsset


class MediaAssetInline(admin.TabularInline):
    model = MediaAsset
    extra = 1
    fields = ("file", "caption")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "kind",
        "discipline",
        "status",
        "is_featured",
        "published_at",
        "views_count",
        "created_at",
    )
    list_filter = ("kind", "discipline", "status", "is_featured", "published_at")
    search_fields = ("title", "excerpt", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
    readonly_fields = ("views_count", "created_at", "updated_at", "published_at")
    inlines = [MediaAssetInline]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("title", "slug", "excerpt", "content"),
            },
        ),
        (
            "Категории и теги",
            {
                "fields": ("categories", "tags"),
            },
        ),
        (
            "Медиа",
            {
                "fields": ("cover", "is_featured"),
            },
        ),
        (
            "Публикация",
            {
                "fields": ("status", "published_at"),
            },
        ),
        (
            "Метаданные",
            {
                "fields": ("author", "views_count", "created_at", "updated_at"),
            },
        ),
    )

    actions = ["action_publish", "action_unpublish"]

    @admin.action(description="Опубликовать выбранные статьи")
    def action_publish(self, request, queryset):
        now = timezone.now()
        queryset.filter(status=Article.STATUS_DRAFT).update(
            status=Article.STATUS_PUBLISHED,
            published_at=now,
        )
        queryset.filter(status=Article.STATUS_PUBLISHED, published_at__isnull=True).update(
            published_at=now,
        )

    @admin.action(description="Снять с публикации выбранные статьи")
    def action_unpublish(self, request, queryset):
        queryset.update(status=Article.STATUS_DRAFT)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author").prefetch_related("categories", "tags")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("article", "caption")
    search_fields = ("article__title", "caption")
