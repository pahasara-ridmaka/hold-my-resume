from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.analytics_view, name="analytics_view"),
    path("export-csv/", views.export_analytics_csv, name='export_analytics_csv'),
]
