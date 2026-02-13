from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_index, name="index"),
    path("articles/", views.article_list, name="article_list"),
    path("articles/create/", views.article_create, name="article_create"),
    path("articles/<int:pk>/edit/", views.article_edit, name="article_edit"),
    path("articles/<int:pk>/delete/", views.article_delete, name="article_delete"),
    path(
        "articles/<int:pk>/toggle-status/",
        views.article_toggle_status,
        name="article_toggle_status",
    ),
]
