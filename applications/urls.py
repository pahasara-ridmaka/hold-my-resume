from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("applications", views.application_list, name="list"),
    path("add/", views.add_application, name="add_application"),
    path("analytics/", views.analytic, name="analytics"),
    path(
        "applications/<uuid:pk>/update-status/",
        views.update_application_status,
        name="update_application_status",
    ),
    path(
        "applications/<uuid:pk>/detail/",
        views.application_detail_drawer,
        name="application_detail_drawer",
    ),
    path("<uuid:pk>/edit/", views.edit_details, name="edit_details"),
]
