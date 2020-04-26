from django.contrib import admin

# Register your models here.

from django.apps import apps
for model in apps.get_app_config('api_v0').models.values():
    admin.site.register(model)
