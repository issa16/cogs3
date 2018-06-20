from django.contrib import admin

from project.forms import ProjectAdminForm
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectSystemAllocation
from project.models import ProjectUserMembership


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(ProjectSystemAllocation)
class ProjectSystemAllocationAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'system',
    )


@admin.register(ProjectUserMembership)
class ProjectUserMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'user',
        'status',
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
