from django.contrib import admin

from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'base_domain',
        'identity_provider',
    )
    search_fields = (
        'name',
        'base_domain',
        'identity_provider',
    )
