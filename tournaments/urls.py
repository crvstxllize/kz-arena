from django.urls import path

from . import views

app_name = "tournaments"

urlpatterns = [
    path("", views.tournament_list, name="tournament_list"),
    path("<str:slug>/", views.tournament_detail, name="tournament_detail"),
]
