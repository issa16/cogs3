from selenium_base import SeleniumTestsBase
from django.core import mail
from project.models import Project


class ProjectIntegrationTests(SeleniumTestsBase):

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
    }


    def test_project(self):
        """
        Create a new project
        Before running this a funding source called test must be added to the database.
        """
        self.sign_in( self.user )

        # Fill the project form with a field missing
        for missing_field in ['id_title','id_description','id_institution','id_start_date','id_end_date']:
            self.get_url("")
            self.click_link_by_url('/projects/create/')
            form_field = dict(self.default_project_form_fields)
            form_field.pop(missing_field)
            self.fill_form_by_id(form_field)
            self.select_from_dropdown_by_id('id_funding_source', 1)
            self.submit_form(self.default_project_form_fields)
            assert "This field is required." in self.selenium.page_source

        self.get_url("")
        self.click_link_by_url('/projects/create/')

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

        #Check the project status
        self.get_url("")
        self.click_link_by_url('/projects/applications/')
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source
        assert 'Awaiting Approval' in self.selenium.page_source

        #Check that the project was created
        matching_projects = Project.objects.filter(title=self.default_project_form_fields['id_title'])
        assert matching_projects.count() == 1

        #Check that the technical lead is the user
        project = matching_projects.first()
        tech_lead_id = project.tech_lead.id
        user_id = self.user.id
        assert tech_lead_id == user_id

        # Check that the project is not active
        status = project.status
        assert status == Project.AWAITING_APPROVAL

        # Approve the project and set a code
        project.status = Project.APPROVED
        project.code = 'code1'
        project.save()

        #Try the Project Applications and Project Memberships pages
        self.get_url("")
        self.click_link_by_url('/projects/applications/')
        assert 'code1' in self.selenium.page_source
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source

        id = project.id
        self.click_link_by_url('/projects/applications/%i/'%id)
        assert self.default_project_form_fields["id_description"] in self.selenium.page_source

        self.get_url("/projects/memberships/")
        assert 'code1' in self.selenium.page_source
        assert self.default_project_form_fields["id_title"] in self.selenium.page_source
        assert 'Project Owner' in self.selenium.page_source

        # Login with a different user (student) and add the project
        self.log_out()
        self.sign_in(self.student)

        self.fill_form_by_id({'project_code': project.code})
        self.submit_form({'project_code': project.code})
        assert 'Successfully submitted a project membership request' in self.selenium.page_source

        #Try an invalid code
        self.get_url("")
        self.fill_form_by_id({'project_code': 'Invalidcode1'})
        self.submit_form({'project_code': project.code})
        assert 'Invalid Project Code' in self.selenium.page_source

        # Check that the project membership is visible
        self.get_url("")
        self.click_link_by_url('/projects/memberships/')
        assert 'Joe Bloggs' in self.selenium.page_source
        assert 'Awaiting Authorisation' in self.selenium.page_source

        # Login with as the tech lead and authorize the new user
        self.log_out()
        self.sign_in(self.user)
        self.get_url("/projects/memberships/user-requests/")

        assert self.student.email in self.selenium.page_source
        self.select_from_first_dropdown(1)

        # Login with student again and check authorisation
        self.log_out()
        self.sign_in(self.student)
        self.get_url("")
        self.click_link_by_url('/projects/memberships/')

        assert 'Authorised' in self.selenium.page_source

        # Set status to rejected and check an email is sent
        project.status = Project.REVOKED
        project.reason_decision = 'A very good reason'
        project.save()

        assert len(mail.outbox) == 1
        # Message should contain the state
        state = project.STATUS_CHOICES[project.status-1][1].lower()
        print(state, mail.outbox[0].message())
        assert state in mail.outbox[0].message()



    def test_create_project_external(self):
        """
        Try to create a project as an external user
        """
        self.sign_in( self.external )
        self.get_url("")
        self.click_link_by_url('/projects/create/')

        self.fill_form_by_id(self.default_project_form_fields)
        self.select_from_dropdown_by_id('id_funding_source', 1)

        self.submit_form(self.default_project_form_fields)

        assert "This field is required." not in self.selenium.page_source
        assert "Successfully submitted a project application." in self.selenium.page_source


    def test_create_project_unauthorized(self):
        """
        Try to create a project without signing in
        """
        #Navigate to the new project form
        self.get_url("/projects/create/")

        #This should throw us to the login page
        assert "accounts/login" in self.selenium.current_url
