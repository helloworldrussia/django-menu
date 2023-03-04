from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import MenuItem, Menu


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    pass


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    pass
