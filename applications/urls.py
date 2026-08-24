from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("", views.application_list, name="application_list"),
    path("<uuid:pk>/resume/", views.view_resume, name="view_resume"),
    path("<uuid:pk>/cover-letter/", views.view_cover_letter, name="view_cover_letter"),
    path("add/", views.add_application, name="add_application"),
    path(
        "<uuid:pk>/update-status/",
        views.update_application_status,
        name="update_application_status",
    ),
    path(
        "<uuid:pk>/detail/",
        views.application_detail_drawer,
        name="application_detail_drawer",
    ),
    path("<uuid:pk>/edit/", views.edit_details, name="edit_details"),
    path("<uuid:pk>/delete/", views.delete_details, name="delete_details"),
]
