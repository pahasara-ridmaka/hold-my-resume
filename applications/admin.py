from django.contrib import admin

from .models import Application, Company, Platform

admin.site.register([Company, Application, Platform])