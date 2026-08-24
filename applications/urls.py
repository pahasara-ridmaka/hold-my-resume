from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("applications", views.application_list, name="application_list"),
    path("applications/<uuid:pk>/resume/", views.view_resume, name="view_resume"),
    path("applications/<uuid:pk>/cover-letter/", views.view_cover_letter, name="view_cover_letter"),
    path("add/", views.add_application, name="add_application"),
    path("analytics/", views.analytics_view, name="analytics"),
    path("analytics/export-csv", views.export_analytics_csv, name='export_analytics_csv'),
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
    path("<uuid:pk>/delete/", views.delete_details, name="delete_details"),
]
