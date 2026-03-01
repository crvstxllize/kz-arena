from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from teams.models import Team

from .models import Match, Tournament


class TournamentPublicPagesTests(TestCase):
    def test_seeded_tournaments_are_rendered_from_database_only(self):
        self.assertEqual(Tournament.objects.count(), 8)
        self.assertEqual(Tournament.objects.filter(is_example=False).count(), 2)
        self.assertEqual(Tournament.objects.filter(is_example=True).count(), 6)

        with patch(
            "lib.data_sync.refresh_sports_data",
            side_effect=AssertionError("External sync must not run for tournaments."),
        ):
            response = self.client.get(reverse("tournaments:tournament_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Astana Open (ATP 250)")
        self.assertContains(response, "Almaty Open")
        self.assertContains(response, "KZ Premier Football Spring (пример)")
        self.assertContains(response, "Пример")
        self.assertContains(response, "Сыграно: 28")
        self.assertNotContains(response, "Источник")
        self.assertNotContains(response, "демо-режима")
        self.assertNotContains(response, "Последнее обновление")


class TournamentDashboardCrudTests(TestCase):
    def setUp(self):
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        self.editor = User.objects.create_user(username="editor", password="pass12345")
        self.editor.groups.add(editors_group)
        self.user = User.objects.create_user(username="user", password="pass12345")

    def test_editor_can_open_tournaments_dashboard_and_create_tournament(self):
        self.client.login(username="editor", password="pass12345")

        list_response = self.client.get(reverse("dashboard:tournament_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Astana Open (ATP 250)")

        create_response = self.client.post(
            reverse("dashboard:tournament_create"),
            {
                "name": "Editor Cup",
                "slug": "editor-cup",
                "kind": Tournament.KIND_ESPORT,
                "discipline": Tournament.DISCIPLINE_CS2,
                "city": "Almaty",
                "venue": "KZ Arena Studio",
                "start_date": "2026-07-01",
                "end_date": "2026-07-03",
                "status": Tournament.STATUS_UPCOMING,
                "description": "Тестовый турнир из dashboard.",
                "is_example": "on",
            },
            follow=True,
        )

        self.assertEqual(create_response.status_code, 200)
        created = Tournament.objects.get(slug="editor-cup")
        self.assertEqual(created.city, "Almaty")
        self.assertTrue(created.is_example)

    def test_regular_user_cannot_access_tournaments_dashboard(self):
        self.client.login(username="user", password="pass12345")

        response = self.client.get(reverse("dashboard:tournament_list"))

        self.assertEqual(response.status_code, 403)


class MatchPublicPagesTests(TestCase):
    def test_seeded_matches_are_rendered_from_database_only(self):
        self.assertEqual(Match.objects.count(), 5)
        self.assertEqual(Match.objects.filter(is_example=False).count(), 2)
        self.assertEqual(Match.objects.filter(is_example=True).count(), 3)

        with patch(
            "lib.data_sync.refresh_sports_data",
            side_effect=AssertionError("External sync must not run for matches."),
        ):
            response = self.client.get(reverse("matches:match_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FC Astana")
        self.assertContains(response, "FC Kairat")
        self.assertContains(response, "1 : 1")
        self.assertNotContains(response, "Источник")
        self.assertNotContains(response, "демо-режим")

    def test_team_detail_shows_upcoming_matches_from_database_only(self):
        team = Team.objects.get(name="FC Astana")

        response = self.client.get(reverse("teams:team_detail", args=[team.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ближайшие матчи")
        self.assertContains(response, "FC Kairat vs FC Astana")
        self.assertNotContains(response, "Источник")


class MatchDashboardCrudTests(TestCase):
    def setUp(self):
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        self.editor = User.objects.create_user(username="editor_match", password="pass12345")
        self.editor.groups.add(editors_group)
        self.user = User.objects.create_user(username="user_match", password="pass12345")

    def test_editor_can_open_matches_dashboard_and_create_match(self):
        self.client.login(username="editor_match", password="pass12345")
        home_team = Team.objects.get(name="FC Astana")
        away_team = Team.objects.get(name="FC Kairat")

        list_response = self.client.get(reverse("dashboard:match_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "FC Astana vs FC Kairat")

        create_response = self.client.post(
            reverse("dashboard:match_create"),
            {
                "title": "Editor Match",
                "kind": Tournament.KIND_SPORT,
                "discipline": Tournament.DISCIPLINE_FOOTBALL,
                "status": Match.STATUS_UPCOMING,
                "start_datetime": "2026-08-01T18:00",
                "venue": "Astana Arena",
                "city": "Astana",
                "home_team": home_team.pk,
                "away_team": away_team.pk,
                "is_example": "on",
            },
            follow=True,
        )

        self.assertEqual(create_response.status_code, 200)
        created = Match.objects.get(title="Editor Match")
        self.assertEqual(created.city, "Astana")
        self.assertTrue(created.is_example)

    def test_regular_user_cannot_access_matches_dashboard(self):
        self.client.login(username="user_match", password="pass12345")

        response = self.client.get(reverse("dashboard:match_list"))

        self.assertEqual(response.status_code, 403)
