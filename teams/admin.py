from django.contrib import admin

from .models import Player, Team


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1
    fields = ("name", "position", "bio", "photo")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "kind",
        "discipline",
        "country",
        "is_manual",
        "is_active",
        "created_at",
    )
    list_filter = ("kind", "discipline", "is_manual", "is_active")
    search_fields = ("name", "country", "city", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (PlayerInline,)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "position")
    list_filter = ("team__discipline", "team__kind")
    search_fields = ("name", "team__name", "position")
