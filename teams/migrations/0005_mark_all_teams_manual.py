from django.db import migrations


def mark_all_teams_manual(apps, schema_editor):
    Team = apps.get_model("teams", "Team")
    Team.objects.filter(is_manual=False).update(is_manual=True)


class Migration(migrations.Migration):
    dependencies = [
        ("teams", "0004_player_last_verified_at_player_source_url"),
    ]

    operations = [
        migrations.RunPython(mark_all_teams_manual, migrations.RunPython.noop),
    ]
