from django.contrib import admin

from .models import Comment, CommentReport


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("text", "user__username")


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "reason", "created_at")
    search_fields = ("reason", "user__username", "comment__text")
