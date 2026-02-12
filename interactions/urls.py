from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("", views.interactions_home, name="index"),
]
