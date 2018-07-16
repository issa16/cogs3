from django.contrib import admin
from funding.models import FundingBody
from funding.models import FundingSource

# Register your models here.


@admin.register(FundingBody)
class FundingBodyAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):
    list_display = ('title', )
