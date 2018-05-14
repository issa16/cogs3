from django.contrib import admin

from .models import Project
from .models import ProjectCategory
from .models import ProjectFundingSource
from .models import ProjectSystemAllocation
from .models import ProjectUserMembership


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
    list_display = (
        'project',
        'user',
        'status',
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'code',
        'institution',
        'tech_lead',
        'status',
    )
    list_filter = (
        'institution',
        'status',
    )
