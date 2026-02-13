from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("", views.api_root, name="root"),
    path("articles/", views.articles_collection, name="articles_collection"),
    path("articles/<int:pk>/", views.article_by_pk, name="article_by_pk"),
    path("articles/<slug:slug>/", views.article_detail, name="article_detail"),
    path("teams/", views.teams_list, name="teams_list"),
    path("tournaments/", views.tournaments_list, name="tournaments_list"),
    path("search/", views.global_search, name="search"),
]
