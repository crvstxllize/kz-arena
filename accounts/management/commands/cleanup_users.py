from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from articles.models import Article


class Command(BaseCommand):
    help = 'Удаляет всех пользователей, кроме суперюзера "kzadmin".'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_user = User.objects.filter(username="kzadmin").first()

        if admin_user is None:
            raise CommandError('Пользователь "kzadmin" не найден. Удаление отменено.')

        if not admin_user.is_superuser:
            raise CommandError('Пользователь "kzadmin" должен быть суперюзером. Удаление отменено.')

        users_to_delete = User.objects.exclude(pk=admin_user.pk)
        deleted_count = users_to_delete.count()

        with transaction.atomic():
            Article.objects.filter(author__in=users_to_delete).update(author=admin_user)
            users_to_delete.delete()

        self.stdout.write(self.style.SUCCESS(f"Удалено пользователей: {deleted_count}"))
        self.stdout.write(self.style.SUCCESS("Остался пользователь: kzadmin"))
