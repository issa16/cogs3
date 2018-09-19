from openldap.api import project_api
from openldap.api import project_membership_api
from project.models import SystemAllocationRequest
from project.models import ProjectUserMembership


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
            project_api.create_project.delay(project=project)
    elif project.status in deactivate_project_states:
        # Check for other approved allocations before deactivating
        if not SystemAllocationRequest.objects.filter(
            project=project,
            status=SystemAllocationRequest.APPROVED
        ).exists:
            project_api.deactivate_project.delay(project=project)


def update_openldap_project_membership(project_membership):
    """
    Ensure project memberships are propagated to OpenLDAP.
    """
    delete_project_membership_states = [
        ProjectUserMembership.REVOKED,
        ProjectUserMembership.SUSPENDED,
    ]
    if project_membership.status == ProjectUserMembership.AUTHORISED:
        project_membership_api.create_project_membership.delay(project_membership=project_membership)
    elif project_membership.status in delete_project_membership_states:
        project_membership_api.delete_project_membership.delay(project_membership=project_membership)
