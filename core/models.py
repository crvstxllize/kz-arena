from django.conf import settings
from django.db import models


class ViewLog(models.Model):
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="view_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="view_logs",
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["article", "-created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"View {self.article_id} at {self.created_at}"
