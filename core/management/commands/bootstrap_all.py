from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap base project data: roles and optional demo seed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Also run seed_demo after bootstrap_roles.",
        )

    def handle(self, *args, **options):
        self.stdout.write("[bootstrap_all] Запуск bootstrap_roles...")
        call_command("bootstrap_roles")

        if options.get("seed"):
            self.stdout.write("[bootstrap_all] Запуск seed_demo...")
            call_command("seed_demo")
        else:
            self.stdout.write("[bootstrap_all] seed_demo пропущен (используйте --seed).")

        self.stdout.write(self.style.SUCCESS("[bootstrap_all] Готово."))
