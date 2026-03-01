from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from articles.models import Article

from .models import Player, Team


class TeamPublicPagesTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass12345")
        self.featured_team = Team.objects.create(
            name="Kairat",
            kind=Team.KIND_SPORT,
            discipline=Team.DISCIPLINE_FOOTBALL,
            description="Основной состав клуба из Алматы.",
            source_url="https://example.com/external-team-source",
            is_manual=False,
            is_active=True,
        )
        Team.objects.create(
            name="Astana",
            kind=Team.KIND_SPORT,
            discipline=Team.DISCIPLINE_FOOTBALL,
            description="Команда из Астаны.",
            is_manual=False,
            is_active=True,
        )
        Team.objects.create(
            name="NOVAQ",
            kind=Team.KIND_ESPORT,
            discipline=Team.DISCIPLINE_CS2,
            description="Основной состав по CS2.",
            is_manual=False,
            is_active=True,
        )
        Team.objects.create(
            name="Golden Barys",
            kind=Team.KIND_ESPORT,
            discipline=Team.DISCIPLINE_DOTA2,
            description="Основной состав по Dota 2.",
            is_manual=False,
            is_active=True,
        )
        example_teams = []
        for index in range(1, 8):
            example_teams.append(
                Team.objects.create(
                    name=f"Extra Team {index}",
                    kind=Team.KIND_ESPORT if index % 2 else Team.KIND_SPORT,
                    discipline=Team.DISCIPLINE_CS2 if index % 2 else Team.DISCIPLINE_BASKETBALL,
                    description=f"Витринная команда {index}.",
                    is_manual=False,
                    is_active=True,
                )
            )
        astana_team = Team.objects.get(name="Astana")
        novaq_team = Team.objects.get(name="NOVAQ")
        golden_barys_team = Team.objects.get(name="Golden Barys")
        for team in [self.featured_team, astana_team, novaq_team, golden_barys_team, *example_teams[:6]]:
            Player.objects.create(
                team=team,
                name=f"Player for {team.name}",
                position="Игрок",
                bio="Тестовый игрок.",
            )
        Team.objects.create(
            name="FC Astana",
            kind=Team.KIND_SPORT,
            discipline=Team.DISCIPLINE_FOOTBALL,
            description="Пустой дубликат без состава.",
            is_manual=False,
            is_active=True,
        )
        Team.objects.create(
            name="Kairat Almaty",
            kind=Team.KIND_SPORT,
            discipline=Team.DISCIPLINE_FOOTBALL,
            description="Пустой дубликат без состава.",
            is_manual=False,
            is_active=True,
        )
        Player.objects.create(
            team=self.featured_team,
            name="Adil Beketov",
            position="Нападающий",
            bio="Игрок основы.",
            source_url="https://example.com/external-player-source",
        )
        Article.objects.create(
            title="Новость о составе Kairat",
            excerpt="Короткий анонс.",
            content="Материал по команде.",
            kind=Article.KIND_SPORT,
            discipline=Team.DISCIPLINE_FOOTBALL,
            status=Article.STATUS_PUBLISHED,
            author=self.author,
        )

    def test_team_list_uses_database_only_and_hides_source_markers(self):
        with patch(
            "lib.data_sync.refresh_sports_data",
            side_effect=AssertionError("External sync must not run for teams list."),
        ):
            response = self.client.get(reverse("teams:team_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kairat")
        self.assertContains(response, "Основной состав клуба из Алматы.")
        self.assertContains(response, "Astana")
        self.assertContains(response, "NOVAQ")
        self.assertContains(response, "Golden Barys")
        self.assertContains(response, "Пример: Extra Team 1")
        self.assertContains(response, "Пример: Extra Team 6")
        self.assertNotContains(response, "Extra Team 7")
        self.assertNotContains(response, "FC Astana")
        self.assertNotContains(response, "Kairat Almaty")
        self.assertContains(response, "placeholders/news/cs2.svg")
        self.assertNotContains(response, "demo-режима")
        self.assertNotContains(response, "Последнее обновление")
        self.assertNotContains(response, "Источник")
        self.assertNotContains(response, "https://example.com/external-team-source")

    def test_team_detail_uses_database_only_and_hides_source_markers(self):
        with patch(
            "lib.data_sync.refresh_sports_data",
            side_effect=AssertionError("External sync must not run for team detail."),
        ):
            response = self.client.get(reverse("teams:team_detail", args=[self.featured_team.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kairat")
        self.assertContains(response, "Adil Beketov")
        self.assertContains(response, "Нападающий")
        self.assertNotContains(response, "данные из открытых источников")
        self.assertNotContains(response, "demo")
        self.assertNotContains(response, "https://example.com/external-team-source")

    def test_example_team_detail_shows_prefixed_name_and_discipline_placeholder(self):
        example_team = Team.objects.get(name="Extra Team 1")

        response = self.client.get(reverse("teams:team_detail", args=[example_team.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пример: Extra Team 1")
        self.assertContains(response, "placeholders/news/cs2.svg")


class TeamDashboardCrudTests(TestCase):
    def setUp(self):
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        self.user = User.objects.create_user(username="editor", password="pass12345")
        self.user.groups.add(editors_group)
        self.team = Team.objects.create(
            name="Golden Barys",
            kind=Team.KIND_ESPORT,
            discipline=Team.DISCIPLINE_DOTA2,
            description="Старое описание.",
            source_url="https://example.com/golden-barys",
            is_manual=False,
            is_active=True,
        )

    def test_dashboard_can_edit_legacy_team_and_persist_changes_in_db(self):
        self.client.login(username="editor", password="pass12345")

        list_response = self.client.get(reverse("dashboard:team_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Golden Barys")

        response = self.client.post(
            reverse("dashboard:team_edit", args=[self.team.pk]),
            {
                "name": "Golden Barys",
                "slug": self.team.slug,
                "kind": Team.KIND_ESPORT,
                "discipline": Team.DISCIPLINE_DOTA2,
                "city": "Almaty",
                "country": "Kazakhstan",
                "description": "Обновлено через dashboard.",
                "source_url": "https://example.com/internal-reference",
                "is_active": "on",
                "members-TOTAL_FORMS": "3",
                "members-INITIAL_FORMS": "0",
                "members-MIN_NUM_FORMS": "0",
                "members-MAX_NUM_FORMS": "1000",
                "members-0-name": "Macao",
                "members-0-position": "Support",
                "members-0-bio": "Игрок состава.",
                "members-1-name": "",
                "members-1-position": "",
                "members-1-bio": "",
                "members-2-name": "",
                "members-2-position": "",
                "members-2-bio": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.team.refresh_from_db()
        self.assertTrue(self.team.is_manual)
        self.assertEqual(self.team.city, "Almaty")
        self.assertEqual(self.team.description, "Обновлено через dashboard.")
        self.assertTrue(self.team.players.filter(name="Macao", position="Support").exists())
