from django.contrib import admin

from .models import Player, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "discipline", "country", "created_at")
    list_filter = ("kind", "discipline")
    search_fields = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "position")
    search_fields = ("name", "team__name")
