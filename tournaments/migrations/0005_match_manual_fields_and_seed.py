from datetime import datetime, timedelta

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import F
from django.utils import timezone


def _local_dt(year, month, day, hour, minute):
    return timezone.make_aware(
        datetime(year, month, day, hour, minute),
        timezone.get_current_timezone(),
    )


def _upcoming_dt(days_offset, hour=19, minute=0):
    base_date = timezone.localdate() + timedelta(days=days_offset)
    return timezone.make_aware(
        datetime.combine(base_date, datetime.min.time()).replace(hour=hour, minute=minute),
        timezone.get_current_timezone(),
    )


def seed_manual_matches(apps, schema_editor):
    Match = apps.get_model("tournaments", "Match")
    MatchResult = apps.get_model("tournaments", "MatchResult")
    Team = apps.get_model("teams", "Team")
    Tournament = apps.get_model("tournaments", "Tournament")

    MatchResult.objects.all().delete()
    Match.objects.all().delete()

    def ensure_team(name, slug, kind, discipline, city="", description="", is_manual=True):
        team, _ = Team.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "kind": kind,
                "discipline": discipline,
                "city": city,
                "country": "Kazakhstan",
                "description": description,
                "is_manual": is_manual,
                "is_active": True,
            },
        )
        changed_fields = []
        if team.name != name:
            team.name = name
            changed_fields.append("name")
        if team.kind != kind:
            team.kind = kind
            changed_fields.append("kind")
        if team.discipline != discipline:
            team.discipline = discipline
            changed_fields.append("discipline")
        if city and team.city != city:
            team.city = city
            changed_fields.append("city")
        if description and team.description != description:
            team.description = description
            changed_fields.append("description")
        if team.is_manual != is_manual:
            team.is_manual = is_manual
            changed_fields.append("is_manual")
        if not team.is_active:
            team.is_active = True
            changed_fields.append("is_active")
        if changed_fields:
            team.save(update_fields=changed_fields)
        return team

    astana = Team.objects.filter(name__iexact="FC Astana").first() or ensure_team(
        name="FC Astana",
        slug="fc-astana",
        kind="sport",
        discipline="football",
        city="Astana",
    )
    kairat = Team.objects.filter(name__iexact="FC Kairat").first() or ensure_team(
        name="FC Kairat",
        slug="fc-kairat",
        kind="sport",
        discipline="football",
        city="Almaty",
    )
    aktobe = Team.objects.filter(name__iexact="FC Aktobe").first() or ensure_team(
        name="FC Aktobe",
        slug="fc-aktobe",
        kind="sport",
        discipline="football",
        city="Aktobe",
        description="Футбольный клуб для ручного управления матчами в KZ Arena.",
    )
    novaq = Team.objects.filter(name__iexact="NOVAQ").first() or ensure_team(
        name="NOVAQ",
        slug="novaq",
        kind="esport",
        discipline="cs2",
        city="Almaty",
        description="Казахстанская команда по Counter-Strike 2.",
    )
    cs2_opponent = (
        Team.objects.filter(kind="esport", discipline="cs2").exclude(pk=getattr(novaq, "pk", None)).first()
    )
    if cs2_opponent is None:
        cs2_opponent = ensure_team(
            name="Example CS2 Team",
            slug="example-cs2-team",
            kind="esport",
            discipline="cs2",
            city="Online",
            description="Пример CS2-команды для ручного управления матчами.",
        )
    golden_barys = Team.objects.filter(name__iexact="Golden Barys").first() or ensure_team(
        name="Golden Barys",
        slug="golden-barys",
        kind="esport",
        discipline="dota2",
        city="Almaty",
        description="Казахстанская команда по Dota 2.",
    )
    dota_opponent = Team.objects.filter(kind="esport", discipline="dota2").exclude(
        pk=getattr(golden_barys, "pk", None)
    ).first()
    if dota_opponent is None:
        dota_opponent = ensure_team(
            name="Example Dota2 Team",
            slug="example-dota2-team",
            kind="esport",
            discipline="dota2",
            city="Online",
            description="Пример команды для демонстрации ручного управления матчами.",
        )

    football_example = Tournament.objects.filter(slug="kz-premier-football-spring-primer").first()
    cs2_example = Tournament.objects.filter(slug="kz-esports-league-cs2-primer").first()
    dota_example = Tournament.objects.filter(slug="central-asia-dota-cup-primer").first()

    matches = [
        {
            "title": "FC Astana vs FC Kairat",
            "kind": "sport",
            "discipline": "football",
            "status": "finished",
            "start_datetime": _local_dt(2025, 3, 2, 14, 0),
            "city": "Astana",
            "venue": "Astana Arena",
            "tournament": None,
            "home_team": astana,
            "away_team": kairat,
            "score_home": 1,
            "score_away": 1,
            "is_example": False,
        },
        {
            "title": "FC Kairat vs FC Aktobe",
            "kind": "sport",
            "discipline": "football",
            "status": "finished",
            "start_datetime": _local_dt(2025, 2, 22, 11, 0),
            "city": "Almaty",
            "venue": "Kazakhstan",
            "tournament": None,
            "home_team": kairat,
            "away_team": aktobe,
            "score_home": 2,
            "score_away": 0,
            "is_example": False,
        },
        {
            "title": "FC Kairat vs FC Astana",
            "kind": "sport",
            "discipline": "football",
            "status": "upcoming",
            "start_datetime": _upcoming_dt(7, 18, 0),
            "city": "Almaty",
            "venue": "Central Stadium, Almaty",
            "tournament": football_example,
            "home_team": kairat,
            "away_team": astana,
            "score_home": None,
            "score_away": None,
            "is_example": True,
        },
        {
            "title": "NOVAQ vs Aktobe Rush",
            "kind": "esport",
            "discipline": "cs2",
            "status": "upcoming",
            "start_datetime": _upcoming_dt(10, 20, 0),
            "city": "Online",
            "venue": "Online",
            "tournament": cs2_example,
            "home_team": novaq,
            "away_team": cs2_opponent,
            "score_home": None,
            "score_away": None,
            "is_example": True,
        },
        {
            "title": "Golden Barys vs Example Dota2 Team",
            "kind": "esport",
            "discipline": "dota2",
            "status": "upcoming",
            "start_datetime": _upcoming_dt(14, 21, 0),
            "city": "Online",
            "venue": "Online",
            "tournament": dota_example,
            "home_team": golden_barys,
            "away_team": dota_opponent,
            "score_home": None,
            "score_away": None,
            "is_example": True,
        },
    ]

    for item in matches:
        Match.objects.update_or_create(
            title=item["title"],
            start_datetime=item["start_datetime"],
            defaults=item,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("teams", "0005_mark_all_teams_manual"),
        ("tournaments", "0004_tournament_matches_count"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="match",
            name="match_team_a_not_equal_team_b",
        ),
        migrations.RemoveIndex(
            model_name="match",
            name="tournaments_tournam_9f6d26_idx",
        ),
        migrations.RemoveIndex(
            model_name="match",
            name="tournaments_status_7d43fe_idx",
        ),
        migrations.RenameField(
            model_name="match",
            old_name="datetime",
            new_name="start_datetime",
        ),
        migrations.RenameField(
            model_name="match",
            old_name="team_a",
            new_name="home_team",
        ),
        migrations.RenameField(
            model_name="match",
            old_name="team_b",
            new_name="away_team",
        ),
        migrations.AddField(
            model_name="match",
            name="title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="match",
            name="kind",
            field=models.CharField(
                blank=True,
                choices=[("sport", "Спорт"), ("esport", "Киберспорт")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="discipline",
            field=models.CharField(
                blank=True,
                choices=[
                    ("football", "Футбол"),
                    ("basketball", "Баскетбол"),
                    ("tennis", "Tennis"),
                    ("cs2", "CS2"),
                    ("dota2", "Dota 2"),
                    ("pubg", "PUBG"),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="venue",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="match",
            name="city",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="match",
            name="score_home",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="score_away",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="is_example",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="match",
            name="created_at",
            field=models.DateTimeField(default=timezone.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="match",
            name="status",
            field=models.CharField(
                choices=[("upcoming", "Скоро"), ("live", "Идет"), ("finished", "Завершен")],
                default="upcoming",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="tournament",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="tournaments.tournament",
            ),
        ),
        migrations.RemoveField(
            model_name="match",
            name="stage",
        ),
        migrations.RemoveField(
            model_name="match",
            name="stream_url",
        ),
        migrations.RemoveField(
            model_name="match",
            name="source_url",
        ),
        migrations.RemoveField(
            model_name="match",
            name="source_updated_at",
        ),
        migrations.AddIndex(
            model_name="match",
            index=models.Index(fields=["tournament", "start_datetime"], name="match_tourn_start_idx"),
        ),
        migrations.AddIndex(
            model_name="match",
            index=models.Index(fields=["status"], name="match_status_idx"),
        ),
        migrations.AddIndex(
            model_name="match",
            index=models.Index(
                fields=["kind", "discipline", "start_datetime"],
                name="match_kind_disc_dt_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                check=~models.Q(home_team=F("away_team")),
                name="match_home_team_not_equal_away_team",
            ),
        ),
        migrations.RunPython(seed_manual_matches, migrations.RunPython.noop),
    ]
