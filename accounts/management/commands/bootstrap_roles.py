from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create base roles for KZ Arena (Editors group)."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Editors")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа Editors создана."))
        else:
            self.stdout.write("Группа Editors уже существует.")

        permissions_count = group.permissions.count()
        self.stdout.write(
            f"Текущих назначенных permissions у Editors: {permissions_count}."
        )
        self.stdout.write(
            self.style.WARNING(
                "Права для редакторов будут расширены после добавления контент-моделей."
            )
        )
