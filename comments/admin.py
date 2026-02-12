from django.contrib import admin

from .models import Comment, CommentReport

admin.site.register(Comment)
admin.site.register(CommentReport)
