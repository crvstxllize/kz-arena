from datetime import datetime, timedelta

from django.db import migrations, models
from django.utils import timezone


TOURNAMENTS = [
    {
        "name": "Astana Open (ATP 250)",
        "slug": "astana-open-atp-250",
        "kind": "sport",
        "discipline": "tennis",
        "city": "Astana",
        "venue": "National Tennis Centre",
        "start_date": datetime(2020, 10, 26).date(),
        "end_date": datetime(2020, 11, 1).date(),
        "status": "finished",
        "description": "Профессиональный теннисный турнир ATP 250 в столице Казахстана.",
        "is_example": False,
    },
    {
        "name": "Almaty Open",
        "slug": "almaty-open",
        "kind": "sport",
        "discipline": "tennis",
        "city": "Almaty",
        "venue": "Almaty Arena",
        "start_date": datetime(2025, 10, 13).date(),
        "end_date": datetime(2025, 10, 19).date(),
        "status": "finished",
        "description": "Теннисный турнир в Алматы (Almaty Arena).",
        "is_example": False,
    },
    {
        "name": "KZ Premier Football Spring (пример)",
        "slug": "kz-premier-football-spring-primer",
        "kind": "sport",
        "discipline": "football",
        "city": "Almaty",
        "venue": "",
        "start_date": datetime(2026, 3, 1).date(),
        "end_date": datetime(2026, 4, 12).date(),
        "status": "upcoming",
        "description": "Демонстрационный турнир для интерфейса футбольного календаря.",
        "is_example": True,
    },
    {
        "name": "Kazakhstan Cup (пример)",
        "slug": "kazakhstan-cup-primer",
        "kind": "sport",
        "discipline": "football",
        "city": "Astana",
        "venue": "",
        "start_date": datetime(2026, 5, 10).date(),
        "end_date": datetime(2026, 6, 15).date(),
        "status": "upcoming",
        "description": "Демонстрационный футбольный кубок для показа турниров в Dashboard и на витрине.",
        "is_example": True,
    },
    {
        "name": "KZ Esports League CS2 (пример)",
        "slug": "kz-esports-league-cs2-primer",
        "kind": "esport",
        "discipline": "cs2",
        "city": "Almaty",
        "venue": "",
        "start_date": datetime(2026, 3, 5).date(),
        "end_date": datetime(2026, 3, 30).date(),
        "status": "upcoming",
        "description": "Демонстрационный киберспортивный турнир по CS2.",
        "is_example": True,
    },
    {
        "name": "Central Asia Dota Cup (пример)",
        "slug": "central-asia-dota-cup-primer",
        "kind": "esport",
        "discipline": "dota2",
        "city": "Shymkent",
        "venue": "",
        "start_date": datetime(2026, 3, 14).date(),
        "end_date": datetime(2026, 3, 29).date(),
        "status": "upcoming",
        "description": "Демонстрационный турнир по Dota 2 для витрины и фильтров.",
        "is_example": True,
    },
    {
        "name": "PUBG Continental Series KZ (пример)",
        "slug": "pubg-continental-series-kz-primer",
        "kind": "esport",
        "discipline": "pubg",
        "city": "Almaty",
        "venue": "",
        "start_date": datetime(2026, 3, 21).date(),
        "end_date": datetime(2026, 4, 6).date(),
        "status": "upcoming",
        "description": "Демонстрационный турнир по PUBG для казахстанской витрины.",
        "is_example": True,
    },
    {
        "name": "Kazakhstan Basketball Events (пример)",
        "slug": "kazakhstan-basketball-events-primer",
        "kind": "sport",
        "discipline": "basketball",
        "city": "Kazakhstan",
        "venue": "",
        "start_date": datetime(2026, 2, 28).date(),
        "end_date": datetime(2026, 2, 28).date(),
        "status": "finished",
        "description": "Демонстрационный турнир по баскетболу для показа finished-состояния.",
        "is_example": True,
    },
]


def seed_manual_tournaments(apps, schema_editor):
    Tournament = apps.get_model("tournaments", "Tournament")
    Tournament.objects.all().delete()

    created_at = timezone.now()
    for index, payload in enumerate(TOURNAMENTS):
        Tournament.objects.create(
            name=payload["name"],
            slug=payload["slug"],
            kind=payload["kind"],
            discipline=payload["discipline"],
            location=payload["city"],
            city=payload["city"],
            venue=payload["venue"],
            start_date=payload["start_date"],
            end_date=payload["end_date"],
            status=payload["status"],
            description=payload["description"],
            is_example=payload["is_example"],
            created_at=created_at + timedelta(seconds=index),
            source_url="",
            source_updated_at=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("tournaments", "0002_match_source_updated_at_match_source_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournament",
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
            model_name="tournament",
            name="city",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="tournament",
            name="venue",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="tournament",
            name="status",
            field=models.CharField(
                choices=[
                    ("upcoming", "Скоро"),
                    ("ongoing", "Идет"),
                    ("finished", "Завершен"),
                ],
                default="upcoming",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="tournament",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="tournament",
            name="is_example",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="tournament",
            name="created_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="tournament",
            options={"ordering": ("-start_date", "-created_at")},
        ),
        migrations.AddIndex(
            model_name="tournament",
            index=models.Index(fields=["status", "is_example"], name="tournaments_status_example_idx"),
        ),
        migrations.RunPython(seed_manual_tournaments, migrations.RunPython.noop),
    ]
