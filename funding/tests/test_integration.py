from selenium_base import SeleniumTestsBase
from funding.models import FundingSource
from institution.models import Institution

from django.urls import reverse


class FundingSourceIntegrationTests(SeleniumTestsBase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def test_create_funding_source_missing_fields(self):
        """
        Try creating a funding source with a required field missing
        """
        self.sign_in(self.user)

        all_form_fields = {
            'id_title': 'Title',
            'id_identifier': 'Id',
            'id_pi_email': self.user.email,
        }

        # Fill the project form with a field missing
        missing_fields = [
            'id_title',
            'id_identifier',
            'id_pi_email',
        ]
        for missing_field in missing_fields:
            self.get_url('')
            self.click_link_by_url(reverse('list-funding-sources'))
            self.click_link_by_url(reverse('create-funding-source'))
            form_field = dict(all_form_fields)
            form_field.pop(missing_field)
            self.fill_form_by_id(form_field)
            self.select_from_dropdown_by_id('id_funding_body', 1)
            self.submit_form(all_form_fields)
            if "This field is required." not in self.selenium.page_source:
                raise AssertionError()

        self.get_url(reverse('list-funding-sources'))
        self.click_link_by_url(reverse('create-funding-source'))
        self.fill_form_by_id(all_form_fields)
        self.submit_form(all_form_fields)
        if "This field is required." not in self.selenium.page_source:
            raise AssertionError()

    def test_create_with_other_pi(self):
        """
        Create a funding source using someone else as the pi
        """
        self.sign_in(self.user)

        institution = Institution.objects.get(name="Example University")
        email = '@'.join(['test', institution.base_domain])

        form_fields = {
            'id_title': 'Title',
            'id_identifier': 'Id',
            'id_pi_email': email,
        }

        self.get_url(reverse('list-funding-sources'))
        self.click_link_by_url(reverse('create-funding-source'))
        self.fill_form_by_id(form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(identifier=form_fields['id_identifier'])
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()
        if funding_source.pi_email != email:
            raise AssertionError()
        if funding_source.pi is not None:
            raise AssertionError()

    def test_create_and_update_funding_source(self):
        """
        Try creating, updating and deleting a funding source
        """
        self.sign_in(self.user)

        form_fields = {
            'id_title': 'Title',
            'id_identifier': 'Id',
            'id_pi_email': self.user.email,
        }

        self.get_url(reverse('list-funding-sources'))
        self.click_link_by_url(reverse('create-funding-source'))
        self.fill_form_by_id(form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(identifier=form_fields['id_identifier'])
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()

        # Check the pi was identified correctly
        if funding_source.pi_email is not None:
            raise AssertionError()
        if funding_source.pi != self.user:
            raise AssertionError()

        # Should be redirected to the list view
        if "funding/list/" not in self.selenium.current_url:
            raise AssertionError()
        if form_fields['id_title'] not in self.selenium.page_source:
            raise AssertionError()

        # Click the update link and edit the title
        self.click_link_by_url(
            reverse(
                'funding-source-update',
                args=[funding_source.id]
            )
        )
        self.fill_form_by_id({'id_title': 'New Title'})
        self.submit_form({'id_title': 'New Title'})
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Should be redirected to the list view again
        if "funding/list/" not in self.selenium.current_url:
            raise AssertionError()
        if 'New Title' not in self.selenium.page_source:
            raise AssertionError()

        # Now delete the funding source
        self.click_link_by_url(
            reverse(
                'delete-funding-source',
                args=[funding_source.id]
            )
        )
        # click 'Delete'
        selector = "//input[@value='Delete']"
        delete_button = self.selenium.find_element_by_xpath(selector)
        delete_button.click()

        # Should be redirected to the list view again
        if "funding/list/" not in self.selenium.current_url:
            raise AssertionError()


        # Check that the funding source was removed
        matching_sources = FundingSource.objects.filter(identifier=form_fields['id_identifier'])
        if matching_sources.count() != 0:
            raise AssertionError()
