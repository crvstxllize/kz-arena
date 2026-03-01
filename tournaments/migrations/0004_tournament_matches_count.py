from django.db import migrations, models


TOURNAMENT_MATCH_COUNTS = {
    "astana-open-atp-250": 28,
    "almaty-open": 28,
    "kz-premier-football-spring-primer": 24,
    "kazakhstan-cup-primer": 16,
    "kz-esports-league-cs2-primer": 18,
    "central-asia-dota-cup-primer": 14,
    "pubg-continental-series-kz-primer": 24,
    "kazakhstan-basketball-events-primer": 6,
}


def seed_matches_count(apps, schema_editor):
    Tournament = apps.get_model("tournaments", "Tournament")
    for slug, matches_count in TOURNAMENT_MATCH_COUNTS.items():
        Tournament.objects.filter(slug=slug).update(matches_count=matches_count)


class Migration(migrations.Migration):
    dependencies = [
        ("tournaments", "0003_tournament_manual_fields_and_seed"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="matches_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(seed_matches_count, migrations.RunPython.noop),
    ]
