from django.conf import settings
from django.db import models
from django.utils import timezone

from core.utils import generate_unique_slug


class Article(models.Model):
    KIND_SPORT = "sport"
    KIND_ESPORT = "esport"
    CONTENT_KIND_CHOICES = [
        (KIND_SPORT, "Спорт"),
        (KIND_ESPORT, "Киберспорт"),
    ]

    DISCIPLINE_FOOTBALL = "football"
    DISCIPLINE_BASKETBALL = "basketball"
    DISCIPLINE_CS2 = "cs2"
    DISCIPLINE_DOTA2 = "dota2"
    DISCIPLINE_PUBG = "pubg"
    DISCIPLINE_CHOICES = [
        (DISCIPLINE_FOOTBALL, "Футбол"),
        (DISCIPLINE_BASKETBALL, "Баскетбол"),
        (DISCIPLINE_CS2, "CS2"),
        (DISCIPLINE_DOTA2, "Dota 2"),
        (DISCIPLINE_PUBG, "PUBG"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Черновик"),
        (STATUS_PUBLISHED, "Опубликовано"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    kind = models.CharField(max_length=20, choices=CONTENT_KIND_CHOICES)
    discipline = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="articles",
    )
    categories = models.ManyToManyField("taxonomy.Category", blank=True, related_name="articles")
    tags = models.ManyToManyField("taxonomy.Tag", blank=True, related_name="articles")
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["kind", "discipline"]),
            models.Index(fields=["is_featured"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)

        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MediaAsset(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    file = models.ImageField(upload_to="article_assets/")
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Asset for {self.article.title}"
