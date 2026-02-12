from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Reaction(models.Model):
    TYPE_LIKE = "like"
    TYPE_DISLIKE = "dislike"
    TYPE_CHOICES = [
        (TYPE_LIKE, "Лайк"),
        (TYPE_DISLIKE, "Дизлайк"),
    ]

    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_LIKE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=["article", "user"], name="unique_reaction_article_user")
        ]

    def __str__(self):
        return f"{self.user} {self.type} {self.article}"


class Favorite(models.Model):
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=["article", "user"], name="unique_favorite_article_user")
        ]

    def __str__(self):
        return f"Избранное {self.user}: {self.article}"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    category = models.ForeignKey(
        "taxonomy.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(team__isnull=False) | models.Q(category__isnull=False),
                name="subscription_team_or_category_required",
            ),
            models.UniqueConstraint(
                fields=["user", "team"],
                condition=models.Q(team__isnull=False),
                name="unique_user_team_subscription",
            ),
            models.UniqueConstraint(
                fields=["user", "category"],
                condition=models.Q(category__isnull=False),
                name="unique_user_category_subscription",
            ),
        ]

    def clean(self):
        super().clean()
        if not self.team and not self.category:
            raise ValidationError("Нужно выбрать команду и/или категорию подписки.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        parts = [str(self.user)]
        if self.team:
            parts.append(f"team={self.team}")
        if self.category:
            parts.append(f"category={self.category}")
        return " | ".join(parts)
