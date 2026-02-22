from django.contrib import admin

from .models import ArticleRating, Favorite, Reaction, Subscription


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "type", "created_at")
    list_filter = ("type",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "category", "created_at")


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "value", "updated_at")
    list_filter = ("value", "updated_at")
    search_fields = ("article__title", "user__username")
