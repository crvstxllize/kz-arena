from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_index, name="index"),
    path("articles/", views.article_list, name="article_list"),
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
