import filecmp
import os
import time

from selenium_base import SeleniumTestsBase

from django.conf import settings
from django.urls import reverse

from project.models import Project
from project.models import ProjectUserMembership


class ProjectIntegrationTests(SeleniumTestsBase):

    settings.MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'tmp')
    settings.MEDIA_URL = '/tmp/'

    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_file.txt')

    default_project_form_fields = {
        "id_title": "Test project",
        "id_description": "This project aims to test the submission of projects",
        "id_institution_reference": "test1",
        "id_department": "SA2C",
        "id_supervisor_name": "Joe Bloggs",
        "id_supervisor_position": "RSE",
        "id_supervisor_email": "joe.bloggs@swan.ac.uk",
        "id_start_date": "2018-09-17",
        "id_end_date": "2019-09-17",
        "id_requirements_software": "none",
        "id_requirements_training": "none",
        "id_requirements_onboarding": "none",
        "id_allocation_cputime": "200",
        "id_allocation_memory": "1",
        "id_allocation_storage_home": "200",
        "id_allocation_storage_scratch": "1",
        'id_document': test_file,
    }

    def test_create_project_missing_fields(self):
        """
        Test project creation and project membership workflows
        """
        self.sign_in(self.user)

        # Fill the project form with a field missing
        missing_fields = [
            'id_title',
            'id_description',
        ]
        for missing_field in missing_fields:
            self.get_url('')
            self.click_link_by_url(reverse('create-project-and-allocation'))
            form_field = dict(self.default_project_form_fields)
            form_field.pop(missing_field)
            self.fill_form_by_id(form_field)
            self.submit_form(self.default_project_form_fields)
            input('wait')
            if "This field is required." not in self.selenium.page_source:
                raise AssertionError()

    def test_create_project(self):

        self.sign_in(self.user)

        self.get_url('')
        self.click_link_by_url(reverse('create-project-and-allocation'))

        # Correctly fill the form
        self.fill_form_by_id(self.default_project_form_fields)
        # self.select_from_dropdown_by_id('id_funding_source', 1)

        # Check that the project does not exist yet
        matching_projects = Project.objects.filter(title=self.default_project_form_fields['id_title'])
        assert matching_projects.count() == 0

        self.submit_form(self.default_project_form_fields)
        input('wait')

        # Add a funding source and include it
        self.click_by_id('fundingsources_dropdown')
        time.sleep(1)
        self.click_link_by_url(reverse('create-funding-source')+'?_popup=1')

        main_window_handle = self.selenium.current_window_handle
        self.selenium.switch_to.window(self.selenium.window_handles[1])

        fundingsource_fields = {
            'id_title': 'Title',
            'id_identifier': 'Id',
            'id_pi_email': self.user.email,
        }
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.fill_form_by_id(fundingsource_fields)
        self.submit_form(fundingsource_fields)

        self.selenium.switch_to.window(main_window_handle)
        self.click_by_id('fundingsources_dropdown')
        time.sleep(1)
        self.click_by_id('id_attributions_0')

        # Add a publication and include it
        self.click_by_id('publication_dropdown')
        time.sleep(1)
        self.click_link_by_url(reverse('create-publication')+'?_popup=1')

        main_window_handle = self.selenium.current_window_handle
        self.selenium.switch_to.window(self.selenium.window_handles[1])

        publication_fields = {
            'id_title': 'Title',
            'id_identifier': 'Id',
        }
        self.fill_form_by_id(publication_fields)
        self.submit_form(publication_fields)

        self.selenium.switch_to.window(main_window_handle)
        self.click_by_id('publication_dropdown')
        time.sleep(1)
        self.click_by_id('id_attributions_1')

        # Submit the form
        self.submit_form(self.default_project_form_fields)

        if "This field is required." in self.selenium.page_source:
            raise AssertionError()
        if "Successfully submitted a project application." not in self.selenium.page_source:
            raise AssertionError()

        # Check the project status
        self.get_url(reverse('project-application-list'))
        if self.default_project_form_fields["id_title"] not in self.selenium.page_source:
            raise AssertionError()
        if 'Awaiting Approval' not in self.selenium.page_source:
            raise AssertionError()

        # Check that the project was created
        matching_projects = Project.objects.filter(title=self.default_project_form_fields['id_title'])
        if matching_projects.count() != 1:
            raise AssertionError()

        # Get the project
        project = matching_projects.first()

        # Check that the technical lead is the user
        tech_lead_id = project.tech_lead.id
        user_id = self.user.id
        if tech_lead_id != user_id:
            raise AssertionError()

        # Check that the project is not active
        if project.status != Project.AWAITING_APPROVAL:
            raise AssertionError()

        # Check that the file was uploaded
        rootpath = os.path.join(os.path.dirname(self.test_file), os.pardir, os.pardir, 'tmp')
        uploadpath = os.path.join(rootpath, project.document.name)
        uploadpath = os.path.normpath(uploadpath)
        if not os.path.isfile(uploadpath):
            raise AssertionError()
        if not filecmp.cmp(uploadpath, self.test_file):
            raise AssertionError()

        # Approve the project and set a code
        project.status = Project.APPROVED
        project.code = 'code1'
        project.save()

        # Check that the user was added to project_owners
        if not self.user.groups.filter(name='project_owner').exists():
            raise AssertionError()

        # Try the Project Applications and Project Memberships pages
        self.get_url(reverse('project-application-list'))
        if 'code1' not in self.selenium.page_source:
            raise AssertionError()
        if self.default_project_form_fields["id_title"] not in self.selenium.page_source:
            raise AssertionError()

        self.click_link_by_url(reverse('project-application-detail', kwargs={'pk': project.id}))
        if self.default_project_form_fields["id_description"] not in self.selenium.page_source:
            raise AssertionError()

        self.get_url(reverse('project-membership-list'))
        if 'code1' not in self.selenium.page_source:
            raise AssertionError()
        if self.default_project_form_fields["id_title"] not in self.selenium.page_source:
            raise AssertionError()
        if 'Project Owner' not in self.selenium.page_source:
            raise AssertionError()

        # Login with a different user (student) and add the project
        self.log_out()
        self.sign_in(self.student)

        self.fill_form_by_id({'project_code': project.code})
        self.submit_form({'project_code': project.code})

        assert ProjectUserMembership.objects.filter(project=project, user=self.student).exists()
        if 'Successfully submitted a project membership request' not in self.selenium.page_source:
            raise AssertionError()

        # Try an invalid code
        self.get_url('')
        self.fill_form_by_id({'project_code': 'Invalidcode1'})
        self.submit_form({'project_code': project.code})
        if 'Invalid Project Code' not in self.selenium.page_source:
            raise AssertionError()

        # Check that the project membership is visible
        self.get_url('')
        self.click_link_by_url(reverse('project-membership-list'))
        if 'Awaiting Authorisation' not in self.selenium.page_source:
            raise AssertionError()

        # Login with as the tech lead and authorize the new user
        self.log_out()
        self.sign_in(self.user)
        self.get_url(reverse('project-user-membership-request-list'))

        if self.student.email not in self.selenium.page_source:
            raise AssertionError()
        self.select_from_first_dropdown(1)

        # Login with student again and check authorisation
        self.log_out()
        self.sign_in(self.student)
        self.get_url('')
        self.click_link_by_url(reverse('project-membership-list'))

        if 'Authorised' not in self.selenium.page_source:
            raise AssertionError()

        # Log in as tech lead and invite a different user
        self.log_out()
        self.sign_in(self.user)
        self.get_url("")
        self.click_link_by_url(reverse('project-application-list'))
        self.click_link_by_url(reverse('project-application-detail',kwargs={'pk': project.id}))
        self.click_link_by_url(reverse('project-membership-invite',kwargs={'pk': project.id}))
        self.fill_form_by_id({'email': self.external.email})
        self.submit_form({'email': self.external.email})

        assert 'Successfully submitted an invitation.' in self.selenium.page_source
        assert ProjectUserMembership.objects.filter(project=project, user=self.external).exists()

        # Check that the request is visible in user-requests
        self.get_url('')
        self.click_link_by_url(reverse('project-user-membership-request-list'))
        assert self.external.email in self.selenium.page_source
        assert 'Awaiting Authorisation' in self.selenium.page_source

        # Login as external and authorise the invitation
        self.log_out()
        self.sign_in(self.external)
        self.click_link_by_url(reverse('project-membership-list'))
        assert project.code in self.selenium.page_source
        self.select_from_first_dropdown(1)

        assert 'Authorised' in self.selenium.page_source

        # Delete the project and check the user was deleted from project_owners
        project.delete()
        if self.user.groups.filter(name='project_owner').exists():
            raise AssertionError()

    def test_create_project_external(self):
        """
        Try to create a project as an external user
        """
        self.sign_in(self.external)
        self.get_url('')

        if "Create Project Application" in self.selenium.page_source:
            raise AssertionError()

    def test_create_project_unauthorized(self):
        """
        Try to create a project without signing in
        """
        # Navigate to the new project form
        self.get_url(reverse('create-project-and-allocation'))

        # This should throw us to the login page
        if "accounts/login" not in self.selenium.current_url:
            raise AssertionError()
