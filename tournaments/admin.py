from django.contrib import admin

from .models import Match, MatchResult, Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "discipline", "start_date", "end_date")
    list_filter = ("kind", "discipline", "start_date")
    search_fields = ("name", "location")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("tournament", "team_a", "team_b", "datetime", "status")
    list_filter = ("status", "tournament")
    search_fields = ("team_a__name", "team_b__name")
    list_select_related = ("tournament", "team_a", "team_b")


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ("match", "score_a", "score_b", "winner")
