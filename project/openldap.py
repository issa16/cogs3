from openldap.api import project_api
from openldap.api import project_membership_api
from project.models import Project
from project.models import ProjectUserMembership


def update_openldap_project(project):
    """
    Ensure project status updates are propagated to OpenLDAP.
    """
    deactivate_project_states = [
        Project.REVOKED,
        Project.SUSPENDED,
        Project.CLOSED,
    ]
    if project.status == Project.APPROVED:
        if project.gid_number:
            project_api.activate_project.delay(project=project)
        else:
            project_api.create_project.delay(project=project)
    elif project.status in deactivate_project_states:
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
