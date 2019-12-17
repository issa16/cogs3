from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException

from funding.models import FundingSource
from institution.models import Institution
from selenium_base import SeleniumTestsBase


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
            'id_amount': '300 000',
            'id_pi_email': self.user.email,
        }

        # Fill the project form with a field missing
        missing_fields = [
            'id_title',
            'id_amount',
            'id_pi_email',
        ]

        # missing identifier field
        self.get_url('')
        self.click_link_by_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')
        self.click_link_by_url(reverse('add-funding-source'))
        self.clear_field_by_id('id_identifier')
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

            # fill first form
            self.fill_form_by_id(identifier_form_fields)
            self.submit_form(identifier_form_fields)

            # fill second form
            self.fill_form_by_id(form_field)
            self.select_from_dropdown_by_id('id_funding_body', 1)
            self.submit_form(all_form_fields)
            if "This field is required." not in self.selenium.page_source:
                raise AssertionError()

        self.get_url(reverse('list-attributions'))
        self.click_by_id('add_attribution_dropdown')
        self.click_link_by_url(reverse('add-funding-source'))

        # fill first form (clear in case browser remembers previous test)
        self.clear_field_by_id('id_identifier')
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

        institution = Institution.objects.get(base_domain="example.ac.uk")
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

        # fill first form (clear in case browser remembers previous test)
        self.clear_field_by_id('id_identifier')
        self.fill_form_by_id(id_form_fields)
        self.submit_form(id_form_fields)

        # fill second form
        self.fill_form_by_id(form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(
            identifier=id_form_fields['id_identifier']
        )
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()
        if funding_source.pi_email != email:
            raise AssertionError(
                'pi_email should be equal to funding source email'
            )
        if funding_source.pi is None or funding_source.pi.email != email:
            raise AssertionError()

    def test_create_funding_source_requiring_approval(self):
        """
        Try creating a funding source with an institution that requires appproval
        """

        # set up the institution to need funding approval and have appropriate templates
        inst = self.user.profile.institution
        inst.needs_funding_approval = True
        inst.funding_document_template = 'Swansea.docx'  # requires an existing document
        inst.funding_document_receiver = 'someone@swan.ac.uk'
        inst.save()

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
        self.clear_field_by_id('id_identifier')
        self.fill_form_by_id(first_form_fields)
        self.submit_form(first_form_fields)

        # Fill and submit second form
        self.fill_form_by_id(second_form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(second_form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(
            identifier=first_form_fields['id_identifier']
        )
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()

        # Check the pi was identified correctly
        if funding_source.pi_email != self.user.email:
            raise AssertionError(
                'funding_source.pi_email is not the same as user email'
            )
        if funding_source.pi != self.user:
            raise AssertionError('funding_source.pi is not a user')

        # Should be redirected to the list view
        if reverse('list-attributions') not in self.selenium.current_url:
            raise AssertionError(
                'current url is not the list-attributions page'
            )
        if second_form_fields['id_title'] not in self.selenium.page_source:
            raise AssertionError()

        # Editing and deleting is only available if the institution
        # Does not require funding approval

        self.user.profile.institution.needs_funding_approval = True
        self.user.profile.institution.save()

        url = reverse('update-attribution', args=[funding_source.id])
        try:
            self.click_link_by_url(url)
        except NoSuchElementException:
            pass
        else:
            raise AssertionError()

    def test_create_funding_source_requiring_approval_with_other_pi(self):
        """
        Create a funding source using someone else as the pi
        """
        from users.models import CustomUser
        email = '@'.join(['pi', self.user.email.split('@')[1]])
        test_pi = CustomUser(
            username=email,
            email=email,
            first_name='test',
            last_name='pi',
            is_staff=False,
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(test_pi)

        self.sign_in(self.user)

        institution_pi = Institution.objects.get(base_domain="example2.ac.uk")
        #email = '@'.join(['test', institution.base_domain])
        email = test_pi.email

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
        self.clear_field_by_id('id_identifier')
        self.fill_form_by_id(id_form_fields)
        self.submit_form(id_form_fields)

        # fill second form
        self.fill_form_by_id(form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(
            identifier=id_form_fields['id_identifier']
        )
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()

        if funding_source.pi_email != email:
            raise AssertionError(
                'pi_email should be equal to current user email'
            )
        if funding_source.pi is None or funding_source.pi.email != email:
            raise AssertionError()

        self.log_out()

        # Manual Approval Step
        funding_source.approved = True
        funding_source.save()

        self.sign_in(test_pi)
        self.get_url(reverse('list-attributions'))
        attrlist_url = self.selenium.current_url

        self.selenium.find_element_by_link_text(form_fields['id_title']).click()

        assert self.selenium.current_url != attrlist_url,\
                    "Pi was redirected to attribution list page "\
                    "instead of the attribution update view."

    def test_create_and_update_funding_source(self):
        """
        Try creating, updating and deleting a funding source
        when approval is not required
        """
        self.user.profile.institution.needs_funding_approval = False
        self.user.profile.institution.save()

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
        self.clear_field_by_id('id_identifier')
        self.fill_form_by_id(first_form_fields)
        self.submit_form(first_form_fields)

        # Fill and submit second form
        self.fill_form_by_id(second_form_fields)
        self.select_from_dropdown_by_id('id_funding_body', 1)
        self.submit_form(second_form_fields)
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Check that the funding source was created
        matching_sources = FundingSource.objects.filter(
            identifier=first_form_fields['id_identifier']
        )
        if matching_sources.count() != 1:
            raise AssertionError()

        # Get the object
        funding_source = matching_sources.get()

        # Check the pi was identified correctly
        if funding_source.pi_email != funding_source.pi.email:
            raise AssertionError(
                'funding_source.pi_email ({}) is not the same as the pi email ({})'.
                format(funding_source.pi_email, funding_source.pi.email)
            )
        if funding_source.pi != self.user:
            raise AssertionError('funding_source.pi is not the current user')

        # Should be redirected to the list view
        if reverse('list-attributions') not in self.selenium.current_url:
            raise AssertionError()

        if second_form_fields['id_title'] not in self.selenium.page_source:
            raise AssertionError()

        # Click the update link and edit the title
        self.click_link_by_url(
            reverse('update-attribution', args=[funding_source.id])
        )
        self.fill_form_by_id({'id_title': 'New Title'})
        self.submit_form({'id_title': 'New Title'})
        if "This field is required." in self.selenium.page_source:
            raise AssertionError()

        # Should be redirected to the list view again
        if reverse('list-attributions') not in self.selenium.current_url:
            raise AssertionError()
        if 'New Title' not in self.selenium.page_source:
            raise AssertionError()

        # Now delete the funding source
        self.click_link_by_url(
            reverse('delete-attribution', args=[funding_source.id])
        )
        # click 'Delete'
        selector = "//input[@value='Delete']"
        delete_button = self.selenium.find_element_by_xpath(selector)
        delete_button.click()

        # Should be redirected to the list view again
        if reverse('list-attributions') not in self.selenium.current_url:
            raise AssertionError()

        # Check that the funding source was removed
        matching_sources = FundingSource.objects.filter(
            identifier=first_form_fields['id_identifier']
        )
        if matching_sources.count() != 0:
            raise AssertionError()
