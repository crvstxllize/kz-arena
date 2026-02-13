from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("add/", views.comment_add_view, name="add"),
    path("delete/", views.comment_delete_view, name="delete"),
    path("list/", views.comment_list_view, name="list"),
]
