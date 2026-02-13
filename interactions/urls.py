from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("react/", views.react_view, name="react"),
    path("favorite/", views.favorite_toggle_view, name="favorite"),
    path("subscribe/", views.subscribe_toggle_view, name="subscribe"),
    path("status/", views.interactions_status_view, name="status"),
]
