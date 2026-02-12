from django.urls import path

from . import views

app_name = "taxonomy"

urlpatterns = [
    path("", views.taxonomy_home, name="index"),
]
