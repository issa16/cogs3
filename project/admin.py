from django.contrib import admin

from project.forms import ProjectAdminForm
from project.forms import ProjectUserMembershipAdminForm
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectSystemAllocation
from project.models import ProjectUserMembership
from project.openldap import update_openldap_project
from project.openldap import update_openldap_project_membership


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

    def _project_membership_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 project membership was'
        else:
            message = '{rows} project memberships were'.format(rows=rows_updated)
        return message

    def activate_project_memberships(self, request, queryset):
        rows_updated = 0
        for membership in queryset:
            membership.status = ProjectUserMembership.AUTHORISED
            membership.save()
            update_openldap_project_membership(membership)
            rows_updated += 1
        message = self._project_membership_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for activation.'.format(message=message))

    activate_project_memberships.short_description = 'Activate selected project memberships in LDAP'

    def deactivate_project_memberships(self, request, queryset):
        rows_updated = 0
        for membership in queryset:
            membership.status = ProjectUserMembership.REVOKED
            membership.save()
            update_openldap_project_membership(membership)
            rows_updated += 1
        message = self._project_membership_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for deactivation.'.format(message=message))

    deactivate_project_memberships.short_description = 'Deactivate selected project memberships in LDAP'

    form = ProjectUserMembershipAdminForm
    actions = [activate_project_memberships, deactivate_project_memberships]
    list_display = (
        'project',
        'user',
        'status',
        'date_joined',
    )
    search_fields = (
        'project__code',
        'user__first_name',
        'user__last_name',
        'user__email',
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    def _project_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 project was'
        else:
            message = '{rows} project were'.format(rows=rows_updated)
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

    activate_projects.short_description = 'Activate selected projects in LDAP'

    def deactivate_projects(self, request, queryset):
        rows_updated = 0
        for project in queryset:
            project.status = Project.REVOKED
            project.save()
            update_openldap_project(project)
            rows_updated += 1
        message = self._project_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for deactivation.'.format(message=message))

    deactivate_projects.short_description = 'Deactivate selected projects in LDAP'

    form = ProjectAdminForm
    actions = [activate_projects, deactivate_projects]

    # Fields to be used when displaying a Project instance.
    list_display = (
        'code',
        'created_time',
        'start_date',
        'tech_lead',
        'status',
    )
    list_filter = ('status', )
    search_fields = (
        'title',
        'legacy_hpcw_id',
        'legacy_arcca_id',
        'code',
        'gid_number',
        'pi',
        'tech_lead__first_name',
        'tech_lead__last_name',
        'tech_lead__email',
    )
