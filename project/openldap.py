import logging

from openldap.api import project_api, project_membership_api
from project.models import ProjectUserMembership, SystemAllocationRequest

logger = logging.getLogger('apps')


def update_openldap_project(allocation):
    """
    Ensure project status updates are propagated to OpenLDAP.
    """
    deactivate_project_states = [
        SystemAllocationRequest.REVOKED,
        SystemAllocationRequest.SUSPENDED,
        SystemAllocationRequest.CLOSED,
    ]

    project = allocation.project

    if allocation.status == SystemAllocationRequest.APPROVED:
        if project.gid_number:
            project_api.activate_project.delay(project=project)
        else:
            project_api.create_project.delay(allocation=allocation)
            activate_existing_users(project)
    elif allocation.status in deactivate_project_states:
        # Check for other approved allocations before deactivating
        num_approved_allocations = SystemAllocationRequest.objects.filter(
            project=project,
            status=SystemAllocationRequest.APPROVED,
        ).count()

        if num_approved_allocations == 1:
            project_api.deactivate_project.delay(allocation=allocation)
        else:
            logger.warning(
                'Failed to deactivate project system allocation request.'
            )


def update_openldap_project_membership(project_membership):
    """
    Ensure project memberships are propagated to OpenLDAP.
    """
    delete_project_membership_states = [
        ProjectUserMembership.REVOKED,
        ProjectUserMembership.SUSPENDED,
    ]
    if not project_membership.project.gid_number:
        if project_membership.status == ProjectUserMembership.AUTHORISED:
            project_membership_api.create_project_membership.delay(
                project_membership=project_membership
            )
        elif project_membership.status in delete_project_membership_states:
            project_membership_api.delete_project_membership.delay(
                project_membership=project_membership
            )


def activate_existing_users(project):
    memberships = ProjectUserMembership.objects.filter(
        project=project, status=ProjectUserMembership.AUTHORISED
    )
    for membership in memberships:
        project_membership_api.create_project_membership.delay(
            project_membership=membership
        )
