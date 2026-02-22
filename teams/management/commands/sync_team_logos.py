from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from teams.assets import resolve_team_logo_asset
from teams.models import Team


class Command(BaseCommand):
    help = "Assign local offline team logos from static assets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing logo values.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated = 0
        skipped = 0
        missing = 0

        for team in Team.objects.order_by("id"):
            asset_path = resolve_team_logo_asset(team.name)
            if not asset_path:
                missing += 1
                self.stdout.write(f"[MISS] {team.name}: mapping not found")
                continue

            src = Path(settings.BASE_DIR) / "static" / asset_path
            if not src.exists():
                missing += 1
                self.stdout.write(f"[MISS] {team.name}: file not found {asset_path}")
                continue

            has_valid_logo = False
            if team.logo and team.logo.name:
                try:
                    has_valid_logo = team.logo.storage.exists(team.logo.name)
                except Exception:
                    has_valid_logo = False

            if has_valid_logo and not force:
                skipped += 1
                self.stdout.write(f"[SKIP] {team.name}: already has logo")
                continue

            with src.open("rb") as logo_file:
                team.logo.save(src.name, File(logo_file), save=False)
            team.save(update_fields=["logo"])
            updated += 1
            self.stdout.write(f"[OK] {team.name} -> {asset_path}")

        self.stdout.write(
            self.style.SUCCESS(
                f"sync_team_logos finished: updated={updated}, skipped={skipped}, missing={missing}"
            )
        )
