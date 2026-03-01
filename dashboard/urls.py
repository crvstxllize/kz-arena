from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_index, name="index"),
    path("articles/", views.article_list, name="article_list"),
    path("teams/", views.team_list, name="team_list"),
    path("tournaments/", views.tournament_list, name="tournament_list"),
    path("matches/", views.match_list, name="match_list"),
    path("teams/create/", views.team_create, name="team_create"),
    path("tournaments/create/", views.tournament_create, name="tournament_create"),
    path("matches/create/", views.match_create, name="match_create"),
    path("teams/<int:pk>/edit/", views.team_edit, name="team_edit"),
    path("tournaments/<int:pk>/edit/", views.tournament_edit, name="tournament_edit"),
    path("matches/<int:pk>/edit/", views.match_edit, name="match_edit"),
    path("teams/<int:pk>/delete/", views.team_delete, name="team_delete"),
    path("tournaments/<int:pk>/delete/", views.tournament_delete, name="tournament_delete"),
    path("matches/<int:pk>/delete/", views.match_delete, name="match_delete"),
    path("articles/search/", views.article_search, name="article_search"),
    path("articles/bulk-delete/", views.article_bulk_delete, name="article_bulk_delete"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/toggle-ban/", views.user_toggle_ban, name="user_toggle_ban"),
    path("users/<int:pk>/set-role/", views.user_set_role, name="user_set_role"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("articles/create/", views.article_create, name="article_create"),
    path("articles/<int:pk>/edit/", views.article_edit, name="article_edit"),
    path("articles/<int:pk>/delete/", views.article_delete, name="article_delete"),
    path(
        "articles/<int:pk>/toggle-status/",
        views.article_toggle_status,
        name="article_toggle_status",
    ),
]
