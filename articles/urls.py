from django.urls import path

from . import views

app_name = "articles"

urlpatterns = [
    path("", views.news_list, name="news_list"),
    path("search/", views.news_search, name="news_search"),
    path("<str:slug>/", views.news_detail, name="news_detail"),
]
