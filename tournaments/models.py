from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

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
    DISCIPLINE_TENNIS = "tennis"
    DISCIPLINE_CS2 = "cs2"
    DISCIPLINE_DOTA2 = "dota2"
    DISCIPLINE_PUBG = "pubg"
    DISCIPLINE_CHOICES = [
        (DISCIPLINE_FOOTBALL, "Футбол"),
        (DISCIPLINE_BASKETBALL, "Баскетбол"),
        (DISCIPLINE_TENNIS, "Tennis"),
        (DISCIPLINE_CS2, "CS2"),
        (DISCIPLINE_DOTA2, "Dota 2"),
        (DISCIPLINE_PUBG, "PUBG"),
    ]

    STATUS_UPCOMING = "upcoming"
    STATUS_ONGOING = "ongoing"
    STATUS_FINISHED = "finished"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Скоро"),
        (STATUS_ONGOING, "Идет"),
        (STATUS_FINISHED, "Завершен"),
    ]

    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=CONTENT_KIND_CHOICES)
    discipline = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES, blank=True)
    location = models.CharField(max_length=180, blank=True)
    city = models.CharField(max_length=120, blank=True)
    venue = models.CharField(max_length=180, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    description = models.TextField(blank=True)
    matches_count = models.PositiveIntegerField(default=0)
    is_example = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(blank=True)
    source_updated_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-start_date", "-created_at")
        indexes = [
            models.Index(fields=["kind", "discipline", "start_date"]),
            models.Index(fields=["status", "is_example"]),
        ]

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "Дата окончания не может быть раньше даты начала."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        if self.city:
            self.location = self.city
        self.full_clean()
        super().save(*args, **kwargs)

    def refresh_status(self, today=None):
        current_date = today or timezone.localdate()
        if self.end_date < current_date:
            self.status = self.STATUS_FINISHED
        elif self.start_date <= current_date <= self.end_date:
            self.status = self.STATUS_ONGOING
        else:
            self.status = self.STATUS_UPCOMING

    @property
    def display_matches_count(self):
        related_matches_count = getattr(self, "matches_count_db", None)
        if related_matches_count is None:
            related_matches_count = self.matches.count() if self.pk else 0
        return max(related_matches_count, self.matches_count)

    @property
    def matches_count_label(self):
        if self.status == self.STATUS_FINISHED:
            return "Сыграно"
        return "Матчей"

    def __str__(self):
        return self.name


class Match(models.Model):
    STATUS_UPCOMING = "upcoming"
    STATUS_LIVE = "live"
    STATUS_FINISHED = "finished"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Скоро"),
        (STATUS_LIVE, "Идет"),
        (STATUS_FINISHED, "Завершен"),
    ]

    title = models.CharField(max_length=255, blank=True)
    kind = models.CharField(max_length=20, choices=Tournament.CONTENT_KIND_CHOICES, blank=True)
    discipline = models.CharField(max_length=20, choices=Tournament.DISCIPLINE_CHOICES, blank=True)
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    start_datetime = models.DateTimeField()
    home_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="matches_as_home",
    )
    away_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="matches_as_away",
    )
    venue = models.CharField(max_length=180, blank=True)
    city = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    score_home = models.PositiveIntegerField(blank=True, null=True)
    score_away = models.PositiveIntegerField(blank=True, null=True)
    is_example = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-start_datetime",)
        indexes = [
            models.Index(fields=["tournament", "start_datetime"], name="match_tourn_start_idx"),
            models.Index(fields=["status"], name="match_status_idx"),
            models.Index(
                fields=["kind", "discipline", "start_datetime"],
                name="match_kind_disc_dt_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(home_team=models.F("away_team")),
                name="match_home_team_not_equal_away_team",
            )
        ]

    def __str__(self):
        return self.title or f"{self.home_team} vs {self.away_team}"

    @property
    def score_display(self):
        if self.score_home is None or self.score_away is None:
            return None
        return f"{self.score_home} : {self.score_away}"

    @property
    def participants_display(self):
        if self.home_team_id and self.away_team_id:
            return f"{self.home_team.name} vs {self.away_team.name}"
        return self.title or "Матч"

    @property
    def location_display(self):
        parts = [item for item in [self.city, self.venue] if item]
        return " · ".join(parts)

    def clean(self):
        super().clean()

        if self.home_team_id and self.away_team_id and self.home_team_id == self.away_team_id:
            raise ValidationError({"away_team": "Гостевая команда должна отличаться от домашней."})

        if self.status == self.STATUS_FINISHED:
            errors = {}
            if self.score_home is None:
                errors["score_home"] = "Для завершенного матча укажите счет."
            if self.score_away is None:
                errors["score_away"] = "Для завершенного матча укажите счет."
            if errors:
                raise ValidationError(errors)

        if self.status == self.STATUS_UPCOMING and (
            self.score_home is not None or self.score_away is not None
        ):
            raise ValidationError(
                {
                    "score_home": "Для будущего матча счет должен быть пустым.",
                    "score_away": "Для будущего матча счет должен быть пустым.",
                }
            )

    def save(self, *args, **kwargs):
        if not self.title and self.home_team_id and self.away_team_id:
            self.title = f"{self.home_team.name} vs {self.away_team.name}"
        if self.tournament_id:
            if not self.kind:
                self.kind = self.tournament.kind
            if not self.discipline:
                self.discipline = self.tournament.discipline
        self.full_clean()
        super().save(*args, **kwargs)


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
        ordering = ("-match__start_datetime",)

    def clean(self):
        super().clean()
        if self.score_a < 0 or self.score_b < 0:
            raise ValidationError("Счет не может быть отрицательным.")

        if self.winner and self.winner_id not in {self.match.home_team_id, self.match.away_team_id}:
            raise ValidationError({"winner": "Победитель должен быть одной из команд матча."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Результат {self.match}"
