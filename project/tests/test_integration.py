from project.models import ProjectFundingSource
from selenium_base import SeleniumTestsBase


class ProjectIntegrationTests(SeleniumTestsBase):

    def fill_project_form(self):
        form_fields = {
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
        self.fill_form_by_id(form_fields)

        self.select_from_dropdown('id_funding_source', 1)
        self.submit_form(form_fields)

    def test_create_project(self):
        """
        Create a new project
        Before running this a funding source called test must be added to the database.
        """
        self.sign_in()
        self.click_by_id("create-project-application-button")

        self.fill_project_form()

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
