from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from funding.models import FundingBody
from funding.models import Attribution
from funding.models import FundingSource
from funding.models import Publication
from funding.models import FundingSourceMembership

# Register your models here.


@admin.register(FundingBody)
class FundingBodyAdmin(SimpleHistoryAdmin):
    list_display = ('name', )


@admin.register(Attribution)
class AttributionAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'created_by', 'owner' )


@admin.register(FundingSourceMembership)
class FundingSourceMembershipnAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'fundingsource', 'approved', )


class FundingSourceMembershipInline(admin.TabularInline):
    model = FundingSourceMembership
    extra = 2


@admin.register(FundingSource)
class FundingSourceAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'pi', 'identifier' )
    inlines = (FundingSourceMembershipInline,)


@admin.register(Publication)
class PublicationAdmin(SimpleHistoryAdmin):
    list_display = ('title', )
