import os
from datetime import date, datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from articles.models import Article
from comments.models import Comment
from core.data.news import NEWS_ITEMS, TOURNAMENT_ITEMS
from interactions.models import Favorite, Reaction, Subscription
from taxonomy.models import Category, Tag
from teams.models import Player, Team
from tournaments.models import Match, MatchResult, Tournament


class Command(BaseCommand):
    help = "Seed demo data for KZ Arena in an idempotent way."

    def handle(self, *args, **options):
        with transaction.atomic():
            editors_group, _ = Group.objects.get_or_create(name="Editors")

            users = self._seed_users(editors_group)
            categories = self._seed_categories()
            tags = self._seed_tags()
            teams = self._seed_teams()
            self._seed_players(teams)
            tournaments = self._seed_tournaments()
            matches = self._seed_matches(tournaments, teams)
            self._seed_match_results(matches, teams)
            articles = self._seed_articles(users, categories, tags)
            self._seed_comments(articles, users)
            self._seed_interactions(articles, users, teams, categories)

        self.stdout.write(self.style.SUCCESS("seed_demo завершен успешно."))
        self.stdout.write(
            f"Users={len(users)} | Categories={Category.objects.count()} | Tags={Tag.objects.count()} | "
            f"Teams={Team.objects.count()} | Players={Player.objects.count()} | "
            f"Tournaments={Tournament.objects.count()} | Matches={Match.objects.count()} | "
            f"Results={MatchResult.objects.count()} | Articles={Article.objects.count()} | "
            f"Comments={Comment.objects.count()} | Reactions={Reaction.objects.count()} | "
            f"Favorites={Favorite.objects.count()} | Subscriptions={Subscription.objects.count()}"
        )

    def _seed_users(self, editors_group):
        specs = [
            ("demo_editor", "editor@kz-arena.local", "Редактор", "KZ"),
            ("demo_user_1", "user1@kz-arena.local", "Айдана", "Серик"),
            ("demo_user_2", "user2@kz-arena.local", "Руслан", "Омаров"),
            ("demo_user_3", "user3@kz-arena.local", "Ильяс", "Тулеу"),
            ("demo_user_4", "user4@kz-arena.local", "Милана", "Жаксылык"),
        ]

        users = []
        for username, email, first_name, last_name in specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                user.set_password("DemoPass123!")
                user.save()
            else:
                changed = False
                if user.email != email:
                    user.email = email
                    changed = True
                if user.first_name != first_name:
                    user.first_name = first_name
                    changed = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    changed = True
                if changed:
                    user.save(update_fields=["email", "first_name", "last_name"])

            users.append(user)

        editors_group.user_set.add(users[0])

        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            users.append(superuser)

        return users

    def _seed_categories(self):
        data = [
            ("Спорт", "Новости традиционных видов спорта Казахстана."),
            ("Киберспорт", "Материалы по CS2, Dota 2 и PUBG."),
            ("Матчи", "Ключевые анонсы и результаты матчей."),
            ("Интервью", "Интервью с игроками и тренерами."),
        ]

        result = {}
        for name, description in data:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            if category.description != description:
                category.description = description
                category.save(update_fields=["description"])
            result[name] = category
        return result

    def _seed_tags(self):
        tag_names = {
            "Казахстан",
            "Футбол",
            "КПЛ",
            "Сборная",
            "Баскетбол",
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

        result = {}
        for name in sorted(tag_names):
            tag, _ = Tag.objects.get_or_create(name=name)
            result[name] = tag
        return result

    def _seed_teams(self):
        data = [
            {
                "name": "Кайрат",
                "kind": "sport",
                "discipline": "football",
                "city": "Алматы",
                "description": "Футбольный клуб. Состав заполнен демо-игроками и требует ручной верификации.",
                "source_url": "https://fckairat.com/",
            },
            {
                "name": "Астана",
                "kind": "sport",
                "discipline": "football",
                "city": "Астана",
                "description": "Футбольный клуб. Состав заполнен демо-игроками и требует ручной верификации.",
                "source_url": "https://fcastana.kz/",
            },
            {
                "name": "Demo: BC Astana (needs review)",
                "kind": "sport",
                "discipline": "basketball",
                "city": "Астана",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "https://pbcastana.kz/",
            },
            {
                "name": "Demo: Irbis Almaty (needs review)",
                "kind": "sport",
                "discipline": "basketball",
                "city": "Алматы",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "",
            },
            {
                "name": "Demo: K23 (needs review)",
                "kind": "esport",
                "discipline": "cs2",
                "city": "Казахстан",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "https://liquipedia.net/counterstrike/K23",
            },
            {
                "name": "Demo: AVANGAR (needs review)",
                "kind": "esport",
                "discipline": "cs2",
                "city": "Казахстан",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "https://liquipedia.net/counterstrike/AVANGAR",
            },
            {
                "name": "Demo: Team Kazakhstan Dota 2 (needs review)",
                "kind": "esport",
                "discipline": "dota2",
                "city": "Казахстан",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "",
            },
            {
                "name": "Demo: Nomad Dota 2 (needs review)",
                "kind": "esport",
                "discipline": "dota2",
                "city": "Казахстан",
                "description": "Требует подтверждения перед публикацией на проде.",
                "source_url": "",
            },
            {
                "name": "Astana Falcons",
                "kind": "sport",
                "discipline": "football",
                "description": "Футбольный клуб из Астаны.",
            },
            {
                "name": "Shymkent United",
                "kind": "sport",
                "discipline": "football",
                "description": "Команда Премьер-лиги Казахстана.",
            },
            {
                "name": "Almaty Hoopers",
                "kind": "sport",
                "discipline": "basketball",
                "description": "Баскетбольный клуб Алматы.",
            },
            {
                "name": "Karaganda Eagles",
                "kind": "sport",
                "discipline": "basketball",
                "description": "Баскетбольная команда Караганды.",
            },
            {
                "name": "Qazaq Wolves",
                "kind": "esport",
                "discipline": "cs2",
                "description": "Профессиональный состав по CS2.",
            },
            {
                "name": "Aktobe Rush",
                "kind": "esport",
                "discipline": "cs2",
                "description": "Казахстанский CS2-коллектив.",
            },
            {
                "name": "Steppe Titans",
                "kind": "esport",
                "discipline": "dota2",
                "description": "Dota 2 команда из Казахстана.",
            },
            {
                "name": "Nomad Fire",
                "kind": "esport",
                "discipline": "pubg",
                "description": "PUBG-ростер с международным опытом.",
            },
            {
                "name": "Altay Phoenix",
                "kind": "esport",
                "discipline": "pubg",
                "description": "PUBG-команда восточного региона.",
            },
        ]

        result = {}
        for item in data:
            team, _ = Team.objects.get_or_create(
                name=item["name"],
                defaults={
                    "kind": item["kind"],
                    "discipline": item["discipline"],
                    "description": item["description"],
                    "city": item.get("city", ""),
                    "source_url": item.get("source_url", ""),
                    "is_manual": True,
                    "is_active": True,
                },
            )
            changed = False
            for field in (
                "kind",
                "discipline",
                "description",
                "city",
                "source_url",
                "is_manual",
                "is_active",
            ):
                incoming_value = item.get(field, True if field in {"is_manual", "is_active"} else "")
                if getattr(team, field) != incoming_value:
                    setattr(team, field, incoming_value)
                    changed = True
            if changed:
                team.save(
                    update_fields=[
                        "kind",
                        "discipline",
                        "description",
                        "city",
                        "source_url",
                        "is_manual",
                        "is_active",
                    ]
                )
            result[item["name"]] = team

        return result

    def _seed_players(self, teams):
        data = [
            ("Нурлан Айтбаев", "Astana Falcons", "Нападающий"),
            ("Алихан Оспанов", "Astana Falcons", "Полузащитник"),
            ("Арсен Төлеубек", "Shymkent United", "Центральный защитник"),
            ("Ерасыл Сагындык", "Almaty Hoopers", "Разыгрывающий"),
            ("Дамир Мусин", "Karaganda Eagles", "Центровой"),
            ("Arman kazeR", "Qazaq Wolves", "Rifler"),
            ("Madi storm", "Qazaq Wolves", "AWPer"),
            ("Roman pixel", "Aktobe Rush", "Entry"),
            ("Bek sultan", "Steppe Titans", "Carry"),
            ("Dias nomad", "Nomad Fire", "IGL"),
            ("Aidar arc", "Altay Phoenix", "Fragger"),
            ("Игрок 1", "Кайрат", "Нападающий"),
            ("Игрок 2", "Кайрат", "Полузащитник"),
            ("Игрок 3", "Кайрат", "Защитник"),
            ("Игрок 4", "Кайрат", "Защитник"),
            ("Игрок 5", "Кайрат", "Вратарь"),
            ("Игрок 1", "Астана", "Нападающий"),
            ("Игрок 2", "Астана", "Полузащитник"),
            ("Игрок 3", "Астана", "Защитник"),
            ("Игрок 4", "Астана", "Защитник"),
            ("Игрок 5", "Астана", "Вратарь"),
            ("Игрок A", "Demo: BC Astana (needs review)", "Guard"),
            ("Игрок B", "Demo: BC Astana (needs review)", "Forward"),
            ("Игрок A", "Demo: K23 (needs review)", "Rifler"),
            ("Игрок B", "Demo: K23 (needs review)", "AWPer"),
            ("Игрок A", "Demo: Team Kazakhstan Dota 2 (needs review)", "Carry"),
            ("Игрок B", "Demo: Team Kazakhstan Dota 2 (needs review)", "Support"),
        ]

        for name, team_name, position in data:
            player, _ = Player.objects.get_or_create(
                name=name,
                team=teams[team_name],
                defaults={
                    "position": position,
                    "bio": f"Игрок команды {team_name}.",
                },
            )
            changed = False
            if player.position != position:
                player.position = position
                changed = True
            if changed:
                player.save(update_fields=["position"])

    def _seed_tournaments(self):
        allowed_names = {item["name"] for item in TOURNAMENT_ITEMS}
        legacy_names = [
            "KZ Premier Football Spring 2026",
            "KZ Esports League CS2 2026",
            "Central Asia Dota Cup 2026",
        ]
        Tournament.objects.filter(name__in=legacy_names).exclude(name__in=allowed_names).delete()

        result = {}
        for item in TOURNAMENT_ITEMS:
            payload = {
                "name": item["name"],
                "kind": item["kind"],
                "discipline": item["discipline"],
                "location": item["location"],
                "start_date": date.fromisoformat(item["start_date"]),
                "end_date": date.fromisoformat(item["end_date"]),
            }
            tournament, _ = Tournament.objects.get_or_create(name=item["name"], defaults=payload)
            changed = False
            for field in ("kind", "discipline", "location", "start_date", "end_date"):
                if getattr(tournament, field) != payload[field]:
                    setattr(tournament, field, payload[field])
                    changed = True
            if changed:
                tournament.save(
                    update_fields=["kind", "discipline", "location", "start_date", "end_date"]
                )
            result[item["name"]] = tournament
        return result

    def _seed_matches(self, tournaments, teams):
        data = [
            (
                "m1",
                "KZ Premier Football Spring",
                "Astana Falcons",
                "Shymkent United",
                datetime(2026, 3, 9, 19, 0),
                "Тур 2",
                "finished",
            ),
            (
                "m2",
                "KZ Premier Football Spring",
                "Shymkent United",
                "Astana Falcons",
                datetime(2026, 3, 16, 18, 0),
                "Тур 3",
                "scheduled",
            ),
            (
                "m3",
                "KZ Esports League CS2",
                "Qazaq Wolves",
                "Aktobe Rush",
                datetime(2026, 3, 24, 19, 0),
                "Полуфинал",
                "finished",
            ),
            (
                "m4",
                "KZ Esports League CS2",
                "Aktobe Rush",
                "Qazaq Wolves",
                datetime(2026, 3, 30, 20, 0),
                "Финал",
                "live",
            ),
            (
                "m5",
                "Central Asia Dota Cup",
                "Steppe Titans",
                "Nomad Fire",
                datetime(2026, 3, 20, 17, 0),
                "Группы",
                "scheduled",
            ),
            (
                "m6",
                "Central Asia Dota Cup",
                "Nomad Fire",
                "Steppe Titans",
                datetime(2026, 3, 28, 18, 0),
                "Плей-офф",
                "scheduled",
            ),
            (
                "m7",
                "PUBG Continental Series",
                "Nomad Fire",
                "Altay Phoenix",
                datetime(2026, 3, 26, 16, 0),
                "Квалификация",
                "finished",
            ),
            (
                "m8",
                "PUBG Continental Series",
                "Altay Phoenix",
                "Nomad Fire",
                datetime(2026, 4, 2, 16, 0),
                "Main Stage",
                "scheduled",
            ),
        ]

        result = {}
        for code, tournament_name, team_a_name, team_b_name, dt, stage, status in data:
            aware_dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            match, _ = Match.objects.get_or_create(
                tournament=tournaments[tournament_name],
                datetime=aware_dt,
                team_a=teams[team_a_name],
                team_b=teams[team_b_name],
                defaults={"stage": stage, "status": status},
            )
            changed = False
            if match.stage != stage:
                match.stage = stage
                changed = True
            if match.status != status:
                match.status = status
                changed = True
            if changed:
                match.save(update_fields=["stage", "status"])
            result[code] = match
        return result

    def _seed_match_results(self, matches, teams):
        data = [
            ("m1", 2, 1, "Astana Falcons"),
            ("m3", 2, 0, "Qazaq Wolves"),
            ("m7", 13, 8, "Nomad Fire"),
        ]

        for code, score_a, score_b, winner_name in data:
            MatchResult.objects.update_or_create(
                match=matches[code],
                defaults={
                    "score_a": score_a,
                    "score_b": score_b,
                    "winner": teams[winner_name],
                },
            )

    def _archive_placeholder_articles(self):
        Article.objects.filter(
            excerpt__icontains="Короткий обзор ключевого события",
            content__icontains="Демо-материал",
        ).update(status=Article.STATUS_DRAFT, is_featured=False)

    def _seed_articles(self, users, categories, tags):
        self._archive_placeholder_articles()

        result = []
        for idx, item in enumerate(NEWS_ITEMS):
            author = users[idx % len(users)]
            kind = Article.KIND_SPORT if item["category"] == "Спорт" else Article.KIND_ESPORT
            published_at = datetime.fromisoformat(item["publishedAt"])
            if timezone.is_naive(published_at):
                published_at = timezone.make_aware(published_at)
            published_at = Article.normalize_publication_datetime(published_at)

            article, _ = Article.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "excerpt": item["excerpt"],
                    "content": item["content"],
                    "kind": kind,
                    "discipline": item["subcategory"],
                    "status": Article.STATUS_PUBLISHED,
                    "author": author,
                    "is_featured": bool(item.get("featured", False)),
                    "published_at": published_at,
                    "views_count": int(item.get("views", 0)),
                },
            )

            changed_fields = []
            for field, value in (
                ("title", item["title"]),
                ("excerpt", item["excerpt"]),
                ("content", item["content"]),
                ("kind", kind),
                ("discipline", item["subcategory"]),
                ("status", Article.STATUS_PUBLISHED),
                ("author", author),
                ("is_featured", bool(item.get("featured", False))),
                ("published_at", published_at),
                ("views_count", int(item.get("views", 0))),
            ):
                current = getattr(article, field)
                compare_value = value.id if field == "author" else value
                current_value = current.id if field == "author" else current
                if current_value != compare_value:
                    setattr(article, field, value)
                    changed_fields.append(field)

            if changed_fields:
                article.save(update_fields=changed_fields)

            article.categories.set([categories[item["category"]]])
            article.tags.set([tags[name] for name in item.get("tags", []) if name in tags])
            self._attach_cover(article, item.get("image"))
            result.append(article)

        result.sort(key=lambda x: x.publication_date_for_display, reverse=True)
        return result

    def _attach_cover(self, article, image_url):
        if not image_url:
            return

        has_cover = bool(article.cover and article.cover.name)
        expected_prefix = f"covers/news-{article.slug}"
        if has_cover and article.cover.name.startswith(expected_prefix):
            return

        try:
            request = Request(image_url, headers={"User-Agent": "KZArenaSeeder/1.0"})
            with urlopen(request, timeout=15) as response:
                raw = response.read()

            parsed = urlparse(image_url)
            ext = os.path.splitext(parsed.path)[1].lower()
            if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                ext = ".jpg"

            file_name = f"news-{article.slug}{ext}"
            article.cover.save(file_name, ContentFile(raw), save=False)
            article.save(update_fields=["cover"])
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(f"Не удалось загрузить обложку для '{article.slug}': {exc}")
            )

    def _seed_comments(self, articles, users):
        templates = [
            "Хороший разбор, особенно по тактике второй половины матча.",
            "Интересно, как это повлияет на таблицу к концу месяца.",
            "Отличный материал, жду превью к следующему туру.",
            "Полезная статистика, спасибо за подробности.",
        ]
        for idx in range(10):
            article = articles[idx % len(articles)]
            user = users[idx % len(users)]
            text = templates[idx % len(templates)]
            Comment.objects.get_or_create(
                article=article,
                user=user,
                text=text,
                defaults={"is_approved": True},
            )

    def _seed_interactions(self, articles, users, teams, categories):
        for idx in range(10):
            Reaction.objects.get_or_create(
                article=articles[idx % len(articles)],
                user=users[idx % len(users)],
                defaults={"type": Reaction.TYPE_LIKE if idx % 4 else Reaction.TYPE_DISLIKE},
            )

        for idx in range(8):
            Favorite.objects.get_or_create(
                article=articles[(idx + 2) % len(articles)],
                user=users[idx % len(users)],
            )

        Subscription.objects.get_or_create(user=users[0], team=teams["Qazaq Wolves"])
        Subscription.objects.get_or_create(user=users[1], team=teams["Astana Falcons"])
        Subscription.objects.get_or_create(user=users[2], category=categories["Киберспорт"])
        Subscription.objects.get_or_create(user=users[3], category=categories["Спорт"])
        Subscription.objects.get_or_create(
            user=users[4],
            team=teams["Nomad Fire"],
            category=categories["Киберспорт"],
        )
