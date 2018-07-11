from django.contrib import admin

from system.models import System
from system.models import SystemToInstitutionMap


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'number_of_cores',
    )
    search_fields = (
        'name',
        'description',
    )


@admin.register(SystemToInstitutionMap)
class SystemToInstitutionMapAdmin(admin.ModelAdmin):
    list_display = (
        'system',
        'institution',
    )
