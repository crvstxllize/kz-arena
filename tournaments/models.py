from django.core.exceptions import ValidationError
from django.db import models

from core.utils import generate_unique_slug


class Tournament(models.Model):
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

    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=CONTENT_KIND_CHOICES)
    discipline = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES, blank=True)
    location = models.CharField(max_length=180, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    source_url = models.URLField(blank=True)
    source_updated_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-start_date",)
        indexes = [models.Index(fields=["kind", "discipline", "start_date"])]

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "Дата окончания не может быть раньше даты начала."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Match(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_LIVE = "live"
    STATUS_FINISHED = "finished"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Запланирован"),
        (STATUS_LIVE, "Идет"),
        (STATUS_FINISHED, "Завершен"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches",
    )
    datetime = models.DateTimeField()
    team_a = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="matches_as_a",
    )
    team_b = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="matches_as_b",
    )
    stage = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    stream_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    source_updated_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-datetime",)
        indexes = [
            models.Index(fields=["tournament", "datetime"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(team_a=models.F("team_b")),
                name="match_team_a_not_equal_team_b",
            )
        ]

    def __str__(self):
        return f"{self.team_a} vs {self.team_b}"


class MatchResult(models.Model):
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name="result",
    )
    score_a = models.PositiveIntegerField()
    score_b = models.PositiveIntegerField()
    winner = models.ForeignKey(
        "teams.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wins",
    )

    class Meta:
        ordering = ("-match__datetime",)

    def clean(self):
        super().clean()
        if self.score_a < 0 or self.score_b < 0:
            raise ValidationError("Счет не может быть отрицательным.")

        if self.winner and self.winner_id not in {self.match.team_a_id, self.match.team_b_id}:
            raise ValidationError({"winner": "Победитель должен быть одной из команд матча."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Результат {self.match}"
