from django.contrib import admin

from .models import System


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'number_of_cores')
