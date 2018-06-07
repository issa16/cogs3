import filecmp
import os

from selenium_base import SeleniumTestsBase

from django.conf import settings
from django.urls import reverse

from project.models import Project


class ProjectIntegrationTests(SeleniumTestsBase):

    settings.MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'tmp')
    settings.MEDIA_URL = '/tmp/'

    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_file.txt')

    default_project_form_fields = {
        "id_title": "Test project",
        "id_description": "This project aims to test the submission of projects",
        "id_institution": "swansea",
        "id_institution_reference": "test1",
        "id_department": "SA2C",
        "id_pi": "Joe Bloggs",
        "id_start_date": "2018-09-17",
        "id_end_date": "2019-09-17",
        "id_requirements_software": "none",
        "id_requirements_gateways": "none",
        "id_requirements_training": "none",
        "id_requirements_onboarding": "none",
        "id_allocation_cputime": "200",
        "id_allocation_memory": "1",
        "id_allocation_storage_home": "200",
        "id_allocation_storage_scratch": "1",
        'id_document': test_file,
    }

    def test_create_project(self):
        """
        Test project creation and project membership workflows
        """
        self.sign_in(self.user)

        # Fill the project form with a field missing
        missing_fields = [
            'id_title',
            'id_description',
            'id_institution',
            'id_start_date',
            'id_end_date',
        ]
        for missing_field in missing_fields:
            self.get_url('')
            self.click_link_by_url(reverse('create-project'))
            form_field = dict(self.default_project_form_fields)
            form_field.pop(missing_field)
            self.fill_form_by_id(form_field)
            self.select_from_dropdown_by_id('id_funding_source', 1)
            self.submit_form(self.default_project_form_fields)
            assert "This field is required." in self.selenium.page_source

        self.get_url('')
        self.click_link_by_url(reverse('create-project'))

        # Correctly fill the form
        self.fill_form_by_id(self.default_project_form_fields)
        self.select_from_dropdown_by_id('id_funding_source', 1)

        # Check that the project does not exist yet
        matching_projects = Project.objects.filter(title=self.default_project_form_fields['id_title'])
        assert matching_projects.count() == 0

        # Submit the form
        self.submit_form(self.default_project_form_fields)

        assert "This field is required." not in self.selenium.page_source
        assert "Successfully submitted a project application." in self.selenium.page_source

        # Check the project status
        self.get_url('')
        self.click_link_by_url(reverse('project-application-list'))
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source
        assert 'Awaiting Approval' in self.selenium.page_source

        # Check that the project was created
        matching_projects = Project.objects.filter(title=self.default_project_form_fields['id_title'])
        assert matching_projects.count() == 1

        # Get the project
        project = matching_projects.first()

        # Check that the technical lead is the user
        tech_lead_id = matching_projects.values_list('tech_lead', flat=True).get(pk=1)
        user_id = self.user.id
        assert tech_lead_id == user_id

        # Check that the project is not active
        status = matching_projects.values_list('status', flat=True).get(pk=1)
        assert status == Project.AWAITING_APPROVAL

        # Check that the file was uploaded
        rootpath = os.path.join(os.path.dirname(self.test_file), os.pardir, os.pardir, 'tmp')
        uploadpath = os.path.join(rootpath, project.document.name)
        uploadpath = os.path.normpath(uploadpath)
        assert os.path.isfile(uploadpath)
        assert filecmp.cmp(uploadpath, self.test_file)

        # Approve the project and set a code
        project.status = Project.APPROVED
        project.code = 'code1'
        project.save()

        # Try the Project Applications and Project Memberships pages
        self.get_url('')
        self.click_link_by_url(reverse('project-application-list'))
        assert 'code1' in self.selenium.page_source
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source

        self.click_link_by_url(reverse('project-application-detail', kwargs={'pk': 1}))
        assert self.default_project_form_fields["id_description"] in self.selenium.page_source

        self.get_url(reverse('project-membership-list'))
        assert 'code1' in self.selenium.page_source
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source
        assert 'Project Owner' in self.selenium.page_source

        # Login with a different user (student) and add the project
        self.log_out()
        self.sign_in(self.student)

        self.fill_form_by_id({'project_code': project.code})
        self.submit_form({'project_code': project.code})
        assert 'Successfully submitted a project membership request' in self.selenium.page_source

        # Try an invalid code
        self.get_url('')
        self.fill_form_by_id({'project_code': 'Invalidcode1'})
        self.submit_form({'project_code': project.code})
        assert 'Invalid Project Code' in self.selenium.page_source

        # Check that the project membership is visible
        self.get_url('')
        self.click_link_by_url(reverse('project-membership-list'))
        assert 'Awaiting Authorisation' in self.selenium.page_source

        # Login with as the tech lead and authorize the new user
        self.log_out()
        self.sign_in(self.user)
        self.get_url(reverse('project-user-membership-request-list'))

        assert self.student.email in self.selenium.page_source
        self.select_from_first_dropdown(1)

        # Login with student again and check authorisation
        self.log_out()
        self.sign_in(self.student)
        self.get_url('')
        self.click_link_by_url(reverse('project-membership-list'))

        assert 'Authorised' in self.selenium.page_source

        # Log in as tech lead and invite a different user
        self.log_out()
        self.sign_in(self.user)
        self.get_url("")
        self.click_link_by_url('/projects/applications/')
        self.click_link_by_url('/projects/applications/%d/' % project.id)
        self.click_link_by_url('/projects/applications/%d/invite-user/' % project.id)
        input('wait')

    def test_create_project_external(self):
        """
        Try to create a project as an external user
        """
        self.sign_in(self.external)
        self.get_url('')
        self.click_link_by_url(reverse('create-project'))

        self.fill_form_by_id(self.default_project_form_fields)
        self.select_from_dropdown_by_id('id_funding_source', 1)

        self.submit_form(self.default_project_form_fields)

        assert "This field is required." not in self.selenium.page_source
        assert "Successfully submitted a project application." in self.selenium.page_source

    def test_create_project_unauthorized(self):
        """
        Try to create a project without signing in
        """
        # Navigate to the new project form
        self.get_url(reverse('create-project'))

        # This should throw us to the login page
        assert "accounts/login" in self.selenium.current_url
