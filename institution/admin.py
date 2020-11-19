from django.contrib import admin

from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    ordering = ('created_time',)
    list_display = (
        'name',
        'base_domain',
        'identity_provider',
        'academic',
        'commercial',
        'service_provider',
        'support_email',
    )
    search_fields = (
        'name',
        'base_domain',
        'identity_provider',
    )
