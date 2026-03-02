from django.core.management.base import BaseCommand

from core.data.news import NEWS_ITEMS
from taxonomy.models import Category, Tag


class Command(BaseCommand):
    help = "Seed base categories and tags required for article forms."

    def handle(self, *args, **options):
        categories_count = self._seed_categories()
        tags_count = self._seed_tags()
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_taxonomy завершен успешно. Categories={categories_count} Tags={tags_count}"
            )
        )

    def _seed_categories(self):
        data = [
            ("Спорт", "Новости традиционных видов спорта Казахстана."),
            ("Киберспорт", "Материалы по CS2, Dota 2 и PUBG."),
            ("Матчи", "Ключевые анонсы и результаты матчей."),
            ("Интервью", "Интервью с игроками и тренерами."),
        ]

        for name, description in data:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            if category.description != description:
                category.description = description
                category.save(update_fields=["description"])

        return Category.objects.count()

    def _seed_tags(self):
        tag_names = {
            "Казахстан",
            "Футбол",
            "КПЛ",
            "Сборная",
            "Баскетбол",
            "Волейбол",
            "Бокс",
            "Борьба",
            "Хоккей",
            "Футзал",
            "Теннис",
            "Кубок",
            "Таблица",
            "Аналитика",
            "CS2",
            "Dota2",
            "PUBG",
            "Киберспорт",
            "Плей-офф",
            "Турниры",
            "PCS",
            "LAN",
            "Трансферы",
            "Матчи",
            "Анонс",
            "Составы",
        }
        for item in NEWS_ITEMS:
            tag_names.update(item.get("tags", []))

        for name in sorted(tag_names):
            Tag.objects.get_or_create(name=name)

        return Tag.objects.count()
