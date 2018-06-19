from django.conf import settings
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

    def _project_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 {company_name} project was'.format(company_name=settings.COMPANY_NAME)
        else:
            message = '{rows} {company_name} project were'.format(
                rows=rows_updated,
                company_name=settings.COMPANY_NAME,
            )
        return message

    def activate_projects(self, request, queryset):
        rows_updated = 0
        for project in queryset:
            project.status = Project.APPROVED
            project.save()
            update_openldap_project(project)
            rows_updated += 1
        message = self._project_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for activation.'.format(message=message))

    activate_projects.short_description = 'Activate selected {company_name} projects'.format(
        company_name=settings.COMPANY_NAME)

    def deactivate_projects(self, request, queryset):
        rows_updated = 0
        for project in queryset:
            project.status = Project.REVOKED
            project.save()
            update_openldap_project(project)
            rows_updated += 1
        message = self._project_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for deactivation.'.format(message=message))

    deactivate_projects.short_description = 'Deactivate selected {company_name} projects'.format(
        company_name=settings.COMPANY_NAME)

    form = ProjectAdminForm
    actions = [activate_projects, deactivate_projects]

    # Fields to be used when displaying a Project instance.
    list_display = (
        'title',
        'code',
        'tech_lead',
        'status',
    )
    list_filter = ('status', )
