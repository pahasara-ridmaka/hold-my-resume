from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth_view, name='login'),
    path('register/', views.auth_view, name='register'),
]