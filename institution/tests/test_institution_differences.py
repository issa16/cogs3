''' 
This tests are written to check the behavioural differences 
between different institutions.

The general idea is to test 

Conditions:
    a. User belongs to a certain institution

Outcomes:
    a. User can/cannot see a certain feature on the web pages 

This is an end-to-end test that checks also the database.
'''

from selenium_base import SeleniumTestsBase
from institution.models import Institution
from users.models import CustomUser

from unittest import skipIf  # DEBUG
from time import sleep  # DEBUG

from django.urls import reverse
import re


class InstitutionDifferencesIntegrationTest(SeleniumTestsBase):

    fixtures = [
        'institution/fixtures/institutions.json',
    ]

    def setUp(self):
        super(InstitutionDifferencesIntegrationTest, self).setUp()

        # There are an Aberystwyth user, a Bangor user, a Cardiff user
        # and a Swansea user

        # For conveninence and for DRY code
        def _createuser(instname):
            institution = Institution.objects.get(name=f"{instname} University")
            # tid : Test Institution Differences
            email = '@'.join(['user_tid', institution.base_domain])
            return CustomUser(
                username=email,
                email=email,
                first_name=instname,
                last_name='User',
                is_staff=False,
                is_shibboleth_login_required=True,
                accepted_terms_and_conditions=True,
            )

        # Create user for Aberystwyth
        self.aberystwyth_user = _createuser(instname='Aberystwyth')
        self.create_test_user(self.aberystwyth_user)

        # Create user for Bangor
        self.bangor_user = _createuser(instname='Bangor')
        self.create_test_user(self.bangor_user)

        # Create user for Cardiff
        self.cardiff_user = _createuser(instname='Cardiff')
        self.create_test_user(self.cardiff_user)

        # Create user for Swansea
        self.swansea_user = _createuser(instname='Swansea')
        self.create_test_user(self.swansea_user)
        self.project_title = 'My Fake Project'

    def _create_fake_project(self, separate_allocation_requests):

        link_text = re.search(
            r'<a href=.*>(.*Create.*Project.*)</a>', self.selenium.page_source
        ).groups()[0]
        self.selenium.find_element_by_link_text(link_text).click()

        fields = {
            'id_title': self.project_title,
            'id_description': 'fake project description',
            'id_supervisor_email': 'pi@aber.ac.uk'
        }

        if not separate_allocation_requests:
            # There should be an allocation section here which requires us
            # to specify the start and end date.
            fields['id_start_date'] = '2019-07-30'
            fields['id_end_date'] = '2019-12-30'

        self.fill_form_by_id(fields)
        self.submit_form(fields)

    def _check_allocation_separation(self, user, separate_allocation_requests):
        # user signs in
        self.sign_in(user)
        # user creates new project
        # We need to find the link to click first
        link_text = re.search(
            r'<a href=.*>(.*Create.*Project.*)</a>', self.selenium.page_source
        ).groups()[0]
        self.selenium.find_element_by_link_text(link_text).click()

        if separate_allocation_requests:
            # There should be no allocation section here:
            if "Allocation" in self.selenium.page_source:
                raise AssertionError('"Allocation" string in page source.')
        else:
            # There should be an allocation section here:
            if "Allocation" not in self.selenium.page_source:
                raise AssertionError('"Allocation" string not in page source.')

        # TODO: we fill the project form using ids
        # TODO: would it be better to use instead labels regexps?
        fields = {
            'id_title': self.project_title,
            'id_description': 'fake project description',
            'id_supervisor_email': 'pi@aber.ac.uk'
        }

        if not separate_allocation_requests:
            # There should be an allocation section here which requires us
            # to specify the start and end date.
            fields['id_start_date'] = '2019-07-30'
            fields['id_end_date'] = '2019-12-30'

        self.fill_form_by_id(fields)
        self.submit_form(fields)

        # this brings us in different places depending on
        # There should be no allocation request section here:
        if "allocation requests" in self.selenium.page_source and not separate_allocation_requests:
            raise AssertionError('"allocation request" string in page source.')

        self.selenium.find_element_by_link_text('Dashboard').click()

        # checking projects
        link_text = re.search(
            r'<a href=.*>(\s*Projects\s*)</a>', self.selenium.page_source
        ).groups()[0]
        self.selenium.find_element_by_link_text(link_text).click()

        # selecting project
        self.selenium.find_element_by_link_text(self.project_title).click()

        if separate_allocation_requests:
            # There should be an allocation request section here:
            if "allocation requests" not in self.selenium.page_source:
                raise AssertionError(
                    '"allocation request" string not in page source.'
                )
        else:
            # There should be no allocation request section here:
            if "allocation requests" in self.selenium.page_source:
                raise AssertionError(
                    '"allocation request" string in page source.'
                )

        self.log_out()

    # Allocation/project separation
    #@skipIf(True,'I want to skip this')
    def test_aberystwyth_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.aberystwyth_user, separate_allocation_requests=False
        )

    #@skipIf(True,'I want to skip this')
    def test_bangor_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.bangor_user, separate_allocation_requests=False
        )

    #@skipIf(True,'I want to skip this')
    def test_cardiff_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.cardiff_user, separate_allocation_requests=False
        )

    #@skipIf(True,'I want to skip this')
    def test_swansea_user_sees_allocation_separation_YES(self):
        self._check_allocation_separation(
            user=self.swansea_user, separate_allocation_requests=True
        )



    def _check_funding_workflow(self,user,need_funding_workflow):
        self.sign_in(user)
        attribution_link_search_res = re.search(
                r'<a href=.*>(\s*Attributions\s*)</a>', self.selenium.page_source
            )
        if need_funding_workflow:
            # There is an Attribution link 
            link_text = attribution_link_search_res.groups()[0]
        else:
            assert attribution_link_search_res is None, 'Attribution link is on the page'

        # TODO: check the rest
 
    # funding workflow
    def test_aberystwyth_user_sees_funding_workflow_YES(self):
        self._check_funding_workflow(self.aberystwyth_user,need_funding_workflow = True)

    #@skipIf(True,'I want to skip this')
    def test_bangor_user_sees_funding_workflow_NO(self):
        self._check_funding_workflow(self.bangor_user,need_funding_workflow = False)
 
    #@skipIf(True,'I want to skip this')
    def test_cardiff_user_sees_funding_workflow_NO(self):
        self._check_funding_workflow(self.cardiff_user,need_funding_workflow = False)
 
    #@skipIf(True,'I want to skip this')
    def test_swansea_user_sees_funding_workflow_YES(self):
        self._check_funding_workflow(self.swansea_user,need_funding_workflow = True)
 
#    # RSE requests
#    @skipIf(True,'I want to skip this')
#    def test_aberystwyth_user_sees_rse_requests_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_bangor_user_sees_rse_requests_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_cardiff_user_sees_rse_requests_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_swansea_user_sees_rse_requests_YES(self):
#        pass
#
#
#    # funding approval
#    @skipIf(True,'I want to skip this')
#    def test_aberystwyth_user_sees_funding_approval_YES(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_bangor_user_sees_funding_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_cardiff_user_sees_funding_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_swansea_user_sees_funding_approval_YES(self):
#        pass
#
#    # supervisor approval
#    @skipIf(True,'I want to skip this')
#    def test_aberystwyth_user_sees_supervisor_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_bangor_user_sees_supervisor_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_cardiff_user_sees_supervisor_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_swansea_user_sees_supervisor_approval_YES(self):
#        pass
#
#    # user approval
#    @skipIf(True,'I want to skip this')
#    def test_aberystwyth_user_sees_user_approval_NO(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_bangor_user_sees_user_approval_YES(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_cardiff_user_sees_user_approval_YES(self):
#        pass
#
#    @skipIf(True,'I want to skip this')
#    def test_swansea_user_sees_user_approval_NO(self):
#        pass
#
#
#
#
