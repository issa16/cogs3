from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from project.forms import (ProjectAdminForm, ProjectUserMembershipAdminForm,
                           SystemAllocationRequestAdminForm)
from project.models import (Project, ProjectCategory, ProjectFundingSource,
                            ProjectSystemAllocation, ProjectUserMembership,
                            RSEAllocation, SystemAllocationRequest)
from project.openldap import (update_openldap_project,
                              update_openldap_project_membership)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name', )


@admin.register(ProjectSystemAllocation)
class ProjectSystemAllocationAdmin(SimpleHistoryAdmin):
    list_display = (
        'project',
        'system',
    )

@admin.register(RSEAllocation)
class RSEAllocationAdmin(SimpleHistoryAdmin):
    list_display = (
        'project',
        'title',
    )

@admin.register(ProjectUserMembership)
class ProjectUserMembershipAdmin(SimpleHistoryAdmin):

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
        'user__profile__scw_username',
    )


@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):

    form = ProjectAdminForm

    # Fields to be used when displaying a Project instance.
    list_display = (
        'code',
        'created_time',
        'tech_lead',
    )
    search_fields = (
        'title',
        'legacy_hpcw_id',
        'legacy_arcca_id',
        'code',
        'gid_number',
        'supervisor_name',
        'supervisor_position',
        'supervisor_email',
        'tech_lead__first_name',
        'tech_lead__last_name',
        'tech_lead__email',
    )


@admin.register(SystemAllocationRequest)
class SystemAllocationRequestAdmin(SimpleHistoryAdmin):

    def _allocation_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 allocation request was'
        else:
            message = '{rows} allocation requests were'.format(rows=rows_updated)
        return message

    def activate_allocations(self, request, queryset):
        rows_updated = 0
        for allocation in queryset:
            allocation.status = SystemAllocationRequest.APPROVED
            allocation.save()
            update_openldap_project(allocation)
            rows_updated += 1
        message = self._allocation_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for activation.'.format(message=message))

    activate_allocations.short_description = 'Activate selected allocations in LDAP'

    def deactivate_allocations(self, request, queryset):
        rows_updated = 0
        for allocation in queryset:
            allocation.status = SystemAllocationRequest.APPROVED
            allocation.save()
            update_openldap_project(allocation)
            rows_updated += 1
        message = self._allocation_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for deactivation.'.format(message=message))

    deactivate_allocations.short_description = 'Deactivate selected allocations in LDAP'

    form = SystemAllocationRequestAdminForm
    actions = [activate_allocations, deactivate_allocations]

    # Fields to be used when displaying a SystemAllocationRequestAdminForm instance.
    list_display = (
        'project',
        'start_date',
        'end_date',
        'allocation_cputime',
    )
