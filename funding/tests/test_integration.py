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

        identifier_form_fields = {
            'id_identifier': 'Id',
        }

        all_form_fields = {
            'id_title': 'Title',
            'id_pi_email': self.user.email,
        }

        # Fill the project form with a field missing
        missing_fields = [
            'id_title',
            'id_pi_email',
        ]

        # missing identifier field
        self.get_url('')
        self.click_link_by_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')
        self.click_link_by_url(reverse('add-funding-source'))
        self.submit_form(identifier_form_fields)
        if "This field is required." not in self.selenium.page_source:
            raise AssertionError()

        # other fields
        for missing_field in missing_fields:
            self.get_url('')
            self.click_link_by_url(reverse('list-attributions'))
            self.click_by_id('add_attribution_dropdown')
            self.click_link_by_url(reverse('add-funding-source'))
            form_field = dict(all_form_fields)
            form_field.pop(missing_field)

            # fill first field
            self.fill_form_by_id(identifier_form_fields)
            self.submit_form(identifier_form_fields)

            # fill second field
            self.fill_form_by_id(form_field)
            self.select_from_dropdown_by_id('id_funding_body', 1)
            self.submit_form(all_form_fields)
            if "This field is required." not in self.selenium.page_source:
                raise AssertionError()

        self.get_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')
        self.click_link_by_url(reverse('add-funding-source'))

        # fill first form
        self.fill_form_by_id(identifier_form_fields)
        self.submit_form(identifier_form_fields)

        # fill in second form
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

        id_form_fields = {
            'id_identifier': 'Id',
        }

        form_fields = {
            'id_title': 'Title',
            'id_pi_email': email,
            'id_amount': 11345234,
        }

        self.get_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')
        self.click_link_by_url(reverse('add-funding-source'))

        # fill first form
        self.fill_form_by_id(id_form_fields)
        self.submit_form(id_form_fields)

        # fill second form
        self.fill_form_by_id(form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(identifier=id_form_fields['id_identifier'])
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()
        if funding_source.pi_email is not None:
            raise AssertionError('pi_email should be None')
        if funding_source.pi is None or funding_source.pi.email != email:
            raise AssertionError()

    def test_create_and_update_funding_source(self):
        """
        Try creating, updating and deleting a funding source
        """
        self.sign_in(self.user)

        first_form_fields = {
            'id_identifier': 'Id',
        }

        second_form_fields = {
            'id_title': 'Title',
            'id_pi_email': self.user.email,
            'id_amount': 11010
        }

        self.get_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')

        # Fill and submit first form
        self.click_link_by_url(reverse('add-funding-source'))
        self.fill_form_by_id(first_form_fields)
        self.submit_form(first_form_fields)

        # Fill and submit second form
        self.fill_form_by_id(second_form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(second_form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(identifier=first_form_fields['id_identifier'])
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()

        # Check the pi was identified correctly
        if funding_source.pi_email is not None:
            raise AssertionError('funding_source.pi_email is not None')
        if funding_source.pi != self.user:
            raise AssertionError('funding_source.pi is not a user')

        # Should be redirected to the list view
        if "funding/list/" not in self.selenium.current_url:
            raise AssertionError()
        if second_form_fields['id_title'] not in self.selenium.page_source:
            raise AssertionError()

        # Click the update link and edit the title
        self.click_link_by_url(
            reverse(
                'update-attribution',
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
                'delete-attribution',
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
        matching_sources = FundingSource.objects.filter(identifier=first_form_fields['id_identifier'])
        if matching_sources.count() != 0:
            raise AssertionError()
