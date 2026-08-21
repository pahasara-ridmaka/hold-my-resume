from django.contrib import admin

from .models import Application, Company

admin.site.register([Company, Application])