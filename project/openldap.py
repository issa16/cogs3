from openldap.api import project_api
from project.models import Project


def update_openldap_project(project):
    """
    Ensure project status updates are propagated to the OpenLDAP project entry.
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
