from django.contrib import admin

from .models import Match, MatchResult, Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "discipline", "city", "status", "is_example", "start_date", "end_date")
    list_filter = ("kind", "discipline", "status", "is_example", "start_date")
    search_fields = ("name", "city", "venue")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "participants_display",
        "tournament",
        "kind",
        "discipline",
        "start_datetime",
        "status",
        "is_example",
    )
    list_filter = ("kind", "discipline", "status", "is_example", "tournament")
    search_fields = ("title", "home_team__name", "away_team__name", "city", "venue")
    list_select_related = ("tournament", "home_team", "away_team")


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ("match", "score_a", "score_b", "winner")
