from django.contrib import admin
from funding.models import FundingBody
from funding.models import Attribution
from funding.models import FundingSource
from funding.models import Publication
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.


@admin.register(FundingBody)
class FundingBodyAdmin(SimpleHistoryAdmin):
    list_display = ('name', )


@admin.register(Attribution)
class AttributionAdmin(SimpleHistoryAdmin):
    list_display = ('title', )


@admin.register(FundingSource)
class FundingSourceAdmin(SimpleHistoryAdmin):
    list_display = ('title', )


@admin.register(Publication)
class PublicationAdmin(SimpleHistoryAdmin):
    list_display = ('title', )
