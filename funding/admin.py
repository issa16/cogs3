from django.contrib import admin
from funding.models import FundingBody
from funding.models import Attribution
from funding.models import FundingSource
from funding.models import Publication

# Register your models here.


@admin.register(FundingBody)
class FundingBodyAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    list_display = ('title', )


@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):
    list_display = ('title', )


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', )
