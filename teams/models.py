from django.db import models

from core.utils import generate_unique_slug


class Team(models.Model):
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

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=CONTENT_KIND_CHOICES)
    discipline = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    country = models.CharField(max_length=80, default="Kazakhstan")
    city = models.CharField(max_length=120, blank=True)
    source_url = models.URLField(blank=True)
    source_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["kind", "discipline"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
    )
    photo = models.ImageField(upload_to="players/", blank=True, null=True)
    position = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["name"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
