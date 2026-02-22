from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create base roles for KZ Arena (Editors group)."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Editors")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа Editors создана."))
        else:
            self.stdout.write("Группа Editors уже существует.")

        editor_permission_codenames = [
            "view_article",
            "add_article",
            "change_article",
            "delete_article",
            "view_mediaasset",
            "add_mediaasset",
            "change_mediaasset",
            "delete_mediaasset",
            "view_category",
            "add_category",
            "change_category",
            "view_tag",
            "add_tag",
            "change_tag",
            "view_comment",
            "change_comment",
            "view_commentreport",
            "view_team",
            "view_player",
            "view_tournament",
            "view_match",
            "view_matchresult",
            "view_reaction",
            "view_favorite",
            "view_subscription",
        ]
        permissions = Permission.objects.filter(codename__in=editor_permission_codenames)
        group.permissions.add(*permissions)

        permissions_count = group.permissions.count()
        self.stdout.write(f"Текущих назначенных permissions у Editors: {permissions_count}.")

        found_codenames = set(permissions.values_list("codename", flat=True))
        missing = sorted(set(editor_permission_codenames) - found_codenames)
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "Не все ожидаемые permissions найдены (возможно, миграции еще не применены): "
                    + ", ".join(missing)
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Базовые permissions для Editors назначены."))

        self.stdout.write(
            "Примечание: доступ в /admin/ требует флага staff; group permissions задают доступ к моделям."
        )
