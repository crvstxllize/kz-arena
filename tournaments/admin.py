from django.contrib import admin

from .models import Match, MatchResult, Tournament

admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(MatchResult)
