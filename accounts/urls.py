from django.urls import path

from . import views

app_name="accounts"

urlpatterns = [
    path('', views.auth_view, name='login'),
    path('register/', views.auth_view, name='register'),
    path('settings/', views.edit_profile, name='edit_profile'),
    path('settings/password/', views.change_password, name='change_password'),
]