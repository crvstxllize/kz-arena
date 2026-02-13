from datetime import date, datetime, timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from articles.models import Article
from comments.models import Comment
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
            comments = self._seed_comments(articles, users)
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
            category, _ = Category.objects.get_or_create(name=name, defaults={"description": description})
            if category.description != description:
                category.description = description
                category.save(update_fields=["description"])
            result[name] = category
        return result

    def _seed_tags(self):
        names = [
            "Казахстан",
            "Плей-офф",
            "CS2",
            "Dota2",
            "PUBG",
            "Футбол",
            "Баскетбол",
            "Трансферы",
            "Рейтинг",
            "Финал",
        ]

        result = {}
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            result[name] = tag
        return result

    def _seed_teams(self):
        data = [
            {"name": "Astana Falcons", "kind": "sport", "discipline": "football", "description": "Футбольный клуб из Астаны."},
            {"name": "Almaty Hoopers", "kind": "sport", "discipline": "basketball", "description": "Баскетбольная команда Алматы."},
            {"name": "Shymkent United", "kind": "sport", "discipline": "football", "description": "Молодой состав южного региона."},
            {"name": "Qazaq Wolves", "kind": "esport", "discipline": "cs2", "description": "Профессиональный состав по CS2."},
            {"name": "Steppe Titans", "kind": "esport", "discipline": "dota2", "description": "Dota 2 коллектив из Астаны."},
            {"name": "Nomad Fire", "kind": "esport", "discipline": "pubg", "description": "PUBG-ростер с международным опытом."},
            {"name": "Karaganda Eagles", "kind": "sport", "discipline": "basketball", "description": "Баскетбольный клуб Караганды."},
            {"name": "Aktobe Rush", "kind": "esport", "discipline": "cs2", "description": "Молодежный состав по CS2."},
        ]

        result = {}
        for item in data:
            team, _ = Team.objects.get_or_create(
                name=item["name"],
                defaults={
                    "kind": item["kind"],
                    "discipline": item["discipline"],
                    "description": item["description"],
                },
            )
            changed = False
            for field in ("kind", "discipline", "description"):
                if getattr(team, field) != item[field]:
                    setattr(team, field, item[field])
                    changed = True
            if changed:
                team.save()
            result[item["name"]] = team

        return result

    def _seed_players(self, teams):
        data = [
            ("Нурлан Айтбаев", "Astana Falcons", "Нападающий"),
            ("Алихан Оспанов", "Astana Falcons", "Полузащитник"),
            ("Ерасыл Сагындык", "Almaty Hoopers", "Разыгрывающий"),
            ("Дамир Мусин", "Karaganda Eagles", "Центровой"),
            ("Arman kazeR", "Qazaq Wolves", "Rifler"),
            ("Madi storm", "Qazaq Wolves", "AWPer"),
            ("Bek sultan", "Steppe Titans", "Carry"),
            ("Dias nomad", "Nomad Fire", "IGL"),
            ("Aruzhan aim", "Aktobe Rush", "Support"),
            ("Roman pixel", "Aktobe Rush", "Entry"),
        ]

        for name, team_name, position in data:
            player, _ = Player.objects.get_or_create(
                name=name,
                defaults={
                    "team": teams[team_name],
                    "position": position,
                    "bio": f"Игрок команды {team_name}.",
                },
            )
            changed = False
            if player.team_id != teams[team_name].id:
                player.team = teams[team_name]
                changed = True
            if player.position != position:
                player.position = position
                changed = True
            if changed:
                player.save()

    def _seed_tournaments(self):
        data = [
            {
                "name": "KZ Premier Football Spring 2026",
                "kind": "sport",
                "discipline": "football",
                "location": "Астана",
                "start_date": date(2026, 3, 1),
                "end_date": date(2026, 4, 12),
            },
            {
                "name": "KZ Esports League CS2 2026",
                "kind": "esport",
                "discipline": "cs2",
                "location": "Алматы",
                "start_date": date(2026, 3, 10),
                "end_date": date(2026, 4, 2),
            },
            {
                "name": "Central Asia Dota Cup 2026",
                "kind": "esport",
                "discipline": "dota2",
                "location": "Шымкент",
                "start_date": date(2026, 4, 5),
                "end_date": date(2026, 4, 18),
            },
        ]

        result = {}
        for item in data:
            tournament, _ = Tournament.objects.get_or_create(name=item["name"], defaults=item)
            changed = False
            for field in ("kind", "discipline", "location", "start_date", "end_date"):
                if getattr(tournament, field) != item[field]:
                    setattr(tournament, field, item[field])
                    changed = True
            if changed:
                tournament.save()
            result[item["name"]] = tournament
        return result

    def _seed_matches(self, tournaments, teams):
        data = [
            ("m1", "KZ Premier Football Spring 2026", "Astana Falcons", "Shymkent United", datetime(2026, 3, 1, 16, 0), "Групповой этап", "finished"),
            ("m2", "KZ Premier Football Spring 2026", "Shymkent United", "Astana Falcons", datetime(2026, 3, 8, 18, 30), "Групповой этап", "scheduled"),
            ("m3", "KZ Esports League CS2 2026", "Qazaq Wolves", "Aktobe Rush", datetime(2026, 3, 10, 19, 0), "Открытие", "finished"),
            ("m4", "KZ Esports League CS2 2026", "Aktobe Rush", "Qazaq Wolves", datetime(2026, 3, 12, 19, 0), "Плей-офф", "live"),
            ("m5", "Central Asia Dota Cup 2026", "Steppe Titans", "Nomad Fire", datetime(2026, 4, 5, 17, 0), "Группы", "scheduled"),
            ("m6", "Central Asia Dota Cup 2026", "Nomad Fire", "Steppe Titans", datetime(2026, 4, 7, 17, 0), "Группы", "scheduled"),
            ("m7", "KZ Premier Football Spring 2026", "Astana Falcons", "Shymkent United", datetime(2026, 3, 15, 20, 0), "Плей-офф", "finished"),
            ("m8", "KZ Esports League CS2 2026", "Qazaq Wolves", "Aktobe Rush", datetime(2026, 3, 18, 18, 0), "Финал", "finished"),
            ("m9", "KZ Premier Football Spring 2026", "Almaty Hoopers", "Karaganda Eagles", datetime(2026, 3, 20, 16, 0), "Товарищеский", "scheduled"),
            ("m10", "KZ Premier Football Spring 2026", "Karaganda Eagles", "Almaty Hoopers", datetime(2026, 3, 28, 16, 0), "Товарищеский", "scheduled"),
        ]

        result = {}
        for code, tournament_name, team_a_name, team_b_name, dt, stage, status in data:
            match, _ = Match.objects.get_or_create(
                tournament=tournaments[tournament_name],
                datetime=timezone.make_aware(dt),
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
            ("m3", 16, 13, "Qazaq Wolves"),
            ("m7", 1, 0, "Astana Falcons"),
            ("m8", 2, 0, "Qazaq Wolves"),
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

    def _seed_articles(self, users, categories, tags):
        now = timezone.now()
        data = [
            ("Астана усилила атаку перед стартом весеннего тура", "sport", "football", ["Спорт", "Матчи"], ["Футбол", "Трансферы"]),
            ("CS2: Qazaq Wolves готовятся к региональному финалу", "esport", "cs2", ["Киберспорт"], ["CS2", "Финал"]),
            ("Баскетбол: Almaty Hoopers выиграли домашнюю серию", "sport", "basketball", ["Спорт"], ["Баскетбол", "Рейтинг"]),
            ("Dota 2: Steppe Titans представили новый драфт-план", "esport", "dota2", ["Киберспорт"], ["Dota2", "Казахстан"]),
            ("PUBG: Nomad Fire поднялись в общем зачете лиги", "esport", "pubg", ["Киберспорт"], ["PUBG", "Рейтинг"]),
            ("Футбол: молодежная академия запускает открытые просмотры", "sport", "football", ["Спорт"], ["Футбол", "Казахстан"]),
            ("CS2: Aktobe Rush изменили тренерский штаб", "esport", "cs2", ["Киберспорт", "Интервью"], ["CS2", "Трансферы"]),
            ("Баскетбол: Karaganda Eagles укрепили защитную линию", "sport", "basketball", ["Спорт"], ["Баскетбол", "Казахстан"]),
            ("Dota 2: расписание Central Asia Cup опубликовано", "esport", "dota2", ["Киберспорт", "Матчи"], ["Dota2", "Финал"]),
            ("Футбольная аналитика: чего ждать от плей-офф", "sport", "football", ["Спорт", "Интервью"], ["Футбол", "Плей-офф"]),
            ("PUBG: команды из Казахстана вышли на LAN-стадию", "esport", "pubg", ["Киберспорт", "Матчи"], ["PUBG", "Плей-офф"]),
            ("Календарь спортивной недели: топ-события в одном списке", "sport", "basketball", ["Спорт", "Матчи"], ["Баскетбол", "Казахстан"]),
        ]

        result = []
        for idx, (title, kind, discipline, category_names, tag_names) in enumerate(data):
            author = users[idx % len(users)]
            article, _ = Article.objects.get_or_create(
                title=title,
                defaults={
                    "excerpt": "Короткий обзор ключевого события и его влияния на сезон.",
                    "content": "Демо-материал для тестирования ORM и будущего вывода ленты новостей.",
                    "kind": kind,
                    "discipline": discipline,
                    "status": Article.STATUS_PUBLISHED,
                    "author": author,
                    "is_featured": idx < 2,
                    "published_at": now - timedelta(hours=idx * 3),
                },
            )

            changed = False
            if article.kind != kind:
                article.kind = kind
                changed = True
            if article.discipline != discipline:
                article.discipline = discipline
                changed = True
            if article.status != Article.STATUS_PUBLISHED:
                article.status = Article.STATUS_PUBLISHED
                changed = True
            if article.author_id != author.id:
                article.author = author
                changed = True
            if article.is_featured != (idx < 2):
                article.is_featured = idx < 2
                changed = True
            if not article.published_at:
                article.published_at = now - timedelta(hours=idx * 3)
                changed = True
            if article.slug == "item" or article.slug.startswith("item-"):
                article.slug = ""
                changed = True
            if changed:
                article.save()

            article.categories.set([categories[name] for name in category_names])
            article.tags.set([tags[name] for name in tag_names])
            result.append(article)

        return result

    def _seed_comments(self, articles, users):
        comments = []
        for idx in range(10):
            article = articles[idx % len(articles)]
            user = users[idx % len(users)]
            text = f"Демо-комментарий #{idx + 1}: отличная новость, ждем продолжения сезона."
            comment, _ = Comment.objects.get_or_create(
                article=article,
                user=user,
                text=text,
                defaults={"is_approved": True},
            )
            comments.append(comment)
        return comments

    def _seed_interactions(self, articles, users, teams, categories):
        for idx in range(8):
            Reaction.objects.get_or_create(
                article=articles[idx % len(articles)],
                user=users[idx % len(users)],
                defaults={"type": Reaction.TYPE_LIKE if idx % 3 else Reaction.TYPE_DISLIKE},
            )

        for idx in range(6):
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
