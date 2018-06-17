from django.contrib import admin

from project.forms import ProjectAdminForm
from project.forms import ProjectUserMembershipAdminForm
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectFundingSource
from project.models import ProjectSystemAllocation
from project.models import ProjectUserMembership


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(ProjectFundingSource)
class ProjectFundingSourceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )


@admin.register(ProjectSystemAllocation)
class ProjectSystemAllocationAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'system',
    )


@admin.register(ProjectUserMembership)
class ProjectUserMembershipAdmin(admin.ModelAdmin):
    form = ProjectUserMembershipAdminForm
    list_display = (
        'user',
        'date_joined',
        'status',
        'project',
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        'title',
        'code',
        'tech_lead',
        'status',
    )
    list_filter = ('status', )
