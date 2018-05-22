from unittest import skip

from project.models import ProjectFundingSource
from selenium_base import SeleniumTestsBase


class ProjectIntegrationTests(SeleniumTestsBase):

    @skip('Pending merge of intergration_tests branch')
    def test_create_project(self):
        """
        Create a new project
        Before running this a funding source called test must be added to the database.
        """
        self.sign_in()
        self.click_by_text('Create Project Application')

        form_fields = {
            "id_title": "Test project",
            "id_description": "This project aims to test the submission of projects",
            "id_institution": "swansea",
            "id_institution_reference": "test1",
            "id_department": "SA2C",
            "id_pi": "Joe Bloggs",
            "id_start_date": "09/15/2018",
            "id_end_date": "05/15/2019",
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

        # scroll to bottom of page to avoid cookie popup in some browsers
        self.scroll_bottom()

        self.click_by_text('Submit')

        assert "This field is required." not in self.selenium.page_source
        assert "Successfully submitted a project application." in self.selenium.page_source
