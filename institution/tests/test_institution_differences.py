''' 
This tests are written to check the behavioural differences 
between different institutions, from the user point of view.
This test focuses only on the differences in the features available,
not on the features themselves, that is: these tests do not check that 
a feature works.

The general idea is to test 

Conditions:
    a. User belongs to a certain institution

Outcomes:
    a. User can/cannot see a certain feature on the web pages 

This is an end-to-end test that checks also the fixtures. 
'''

from selenium_base import SeleniumTestsBase
from institution.models import Institution
from project.models import Project, SystemAllocationRequest
import project  # TENTATIVE
from system.models import System
from users.models import CustomUser

from unittest import skipIf
from mock import Mock, patch

from django.urls import reverse
from django.test import tag
from selenium.common.exceptions import NoSuchElementException
from django.utils.translation import gettext_lazy as _
import re


class InstitutionDifferencesIntegrationTest(SeleniumTestsBase):

    fixtures = [
        'institution/fixtures/institutions.json',
    ]

    def setUp(self):
        super(InstitutionDifferencesIntegrationTest, self).setUp()

        # There are an Aberystwyth user, a Bangor user, a Cardiff user
        # and a Swansea user

        # USERS WITH AUTHORISATION
        # Create user for Aberystwyth
        self.aberystwyth_user = self._createuser(instname='Aberystwyth')
        self.create_test_user(self.aberystwyth_user)

        # Create user for Bangor
        self.bangor_user = self._createuser(instname='Bangor')
        self.create_test_user(self.bangor_user)

        # Create user for Cardiff
        self.cardiff_user = self._createuser(instname='Cardiff')
        self.create_test_user(self.cardiff_user)

        # Create user for Swansea
        self.swansea_user = self._createuser(instname='Swansea')
        self.create_test_user(self.swansea_user)

        # USERS AWAITING AUTHORISATION
        # Create user for Aberystwyth
        self.aberystwyth_user_aa = self._createuser(
            instname='Aberystwyth', username='user_tid_aa'
        )
        self._create_test_user_unapproved(self.aberystwyth_user_aa)

        # Create user for Bangor
        self.bangor_user_aa = self._createuser(
            instname='Bangor', username='user_tid_aa'
        )
        self._create_test_user_unapproved(self.bangor_user_aa)

        # Create user for Cardiff
        self.cardiff_user_aa = self._createuser(
            instname='Cardiff', username='user_tid_aa'
        )
        self._create_test_user_unapproved(self.cardiff_user_aa)

        # Create user for Swansea
        self.swansea_user_aa = self._createuser(
            instname='Swansea', username='user_tid_aa'
        )
        self._create_test_user_unapproved(self.swansea_user_aa)

        self.fake_project_title = 'My Fake Project'
        self.local_institutional_identifier = 'A Local Institutional Identifier'

    def _create_test_user_unapproved(self, user):
        user.set_password(self.user_password)
        domain = user.email.split('@')[1]
        user.save()

    # For conveninence and for DRY code
    def _createuser(self, instname, username='user_tid'):
        institution = Institution.objects.get(name=f"{instname} University")
        # tid : Test Institution Differences
        email = '@'.join([username, institution.base_domain])
        return CustomUser(
            username=email,
            email=email,
            first_name=instname,
            last_name='User',
            is_staff=False,
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )

    def _go_to_dashboard(self):
        self.selenium.find_element_by_link_text('Dashboard').click()

    def _go_to_project_creation_from_dashboard(self):
        # We need to find the link to click first
        link_text = re.search(
            r'<a href=.*>(.*Create.*Project.*)</a>', self.selenium.page_source
        ).groups()[0]
        self.selenium.find_element_by_link_text(link_text).click()

    def _go_to_project_list_from_dashboard(self):
        link_text = re.search(
            r'<a href=.*>(\s*Projects\s*)</a>', self.selenium.page_source
        ).groups()[0]
        self.selenium.find_element_by_link_text(link_text).click()

    def _select_or_create_fake_project_in_project_list(
        self, separate_allocation_requests, project_owner
    ):
        try:
            el = self.selenium.find_element_by_link_text(
                self.fake_project_title
            )
        except NoSuchElementException:
            self._create_fake_project_via_ui(
                separate_allocation_requests, project_owner
            )
            self._go_to_dashboard()
            self._go_to_project_list_from_dashboard()
            el = self.selenium.find_element_by_link_text(
                self.fake_project_title
            )
        el.click()

    def _create_fake_project_via_ui(
        self, separate_allocation_requests, project_owner
    ):

        self._go_to_dashboard()
        self._go_to_project_creation_from_dashboard()

        fields = {
            'id_title': self.fake_project_title,
            'id_description': 'fake project description - from UI',
            'id_supervisor_email': 'pi@aber.ac.uk'
        }

        if not separate_allocation_requests:
            # There should be an allocation section here which requires us
            # to specify the start and end date.
            fields['id_start_date'] = '2019-07-30'
            fields['id_end_date'] = '2019-12-30'

        self.fill_form_by_id(fields)
        self.submit_form(fields)

    def _create_fake_project_approved(self, project_owner):
        fake_project = Project.objects.create(
            title=self.fake_project_title,
            description='fake project description',
            supervisor_email="pi@aber.ac.uk",
            tech_lead=project_owner,
            #category=ProjectCategory.objects.get(id=1)  # a random one
        )
        fake_project.save()

        # we create a fake system allocation request which is approved from the
        # very beginning, so that the project should be approved
        fake_system_allocation_request = SystemAllocationRequest(
            project=fake_project,
            start_date='2019-08-20',
            end_date='2019-12-31',
            status=Project.APPROVED
        )
        fake_system_allocation_request.save()
        assert fake_project.is_approved()

    # Allocation/project separation
    def _check_allocation_separation(self, user, separate_allocation_requests):
        # user signs in
        self.sign_in(user)
        self._go_to_project_creation_from_dashboard()

        # user creates new project
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
            'id_title': self.fake_project_title,
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

        self._go_to_dashboard()
        self._go_to_project_list_from_dashboard()
        # selecting project
        self.selenium.find_element_by_link_text(self.fake_project_title).click()

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

    @tag("proj_alloc_sep")
    def test_aberystwyth_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.aberystwyth_user, separate_allocation_requests=False
        )

    @tag("proj_alloc_sep")
    def test_bangor_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.bangor_user, separate_allocation_requests=False
        )

    @tag("proj_alloc_sep")
    def test_cardiff_user_sees_allocation_separation_NO(self):
        self._check_allocation_separation(
            user=self.cardiff_user, separate_allocation_requests=False
        )

    @tag("proj_alloc_sep")
    def test_swansea_user_sees_allocation_separation_YES(self):
        self._check_allocation_separation(
            user=self.swansea_user, separate_allocation_requests=True
        )

    def _check_funding_workflow(
        self, user, need_funding_workflow, separate_allocation_requests
    ):
        self.sign_in(user)

        # check the dashboard
        attribution_link_search_res = re.search(
            r'<a href=.*>(\s*Attributions\s*)</a>', self.selenium.page_source
        )
        if need_funding_workflow:
            # There is an Attribution link
            link_text = attribution_link_search_res.groups()[0]
        else:
            # there should be no mentions of Attributions
            assert attribution_link_search_res is None, 'Attribution link is on the page'

        # check the project creation form
        self._go_to_project_creation_from_dashboard()

        match = re.search('[fF]unding\s+[sS]ources', self.selenium.page_source)
        if need_funding_workflow:
            # There is mention of Funding sources and grants
            assert match is not None, 'No mention of funding sources in page source'
        else:
            assert match is None, 'Funding sources should not be mentioned in page source'

        self._go_to_dashboard()
        self._go_to_project_list_from_dashboard()
        # selecting project
        self._select_or_create_fake_project_in_project_list(
            separate_allocation_requests, project_owner=user
        )

        # checking that there is/there is not 'Attributions' in the page source.
        match = re.search('[Aa]ttributions', self.selenium.page_source)
        if need_funding_workflow:
            # There is mention of Attributions
            assert match is not None, 'No mention of Attributions in page source'
            # There is a 'manage attributions' link
            try:
                el = self.selenium.find_element_by_link_text(
                    "Manage attributions"
                )
            except NoSuchElementException:
                raise AssertionError(
                    'A "Manage Attributions" link should be present'
                )
        else:
            assert match is None, 'Attributions should not be mentioned in page source'

    @tag("fund_wf")
    def test_aberystwyth_user_sees_funding_workflow_YES(self):
        self._check_funding_workflow(
            self.aberystwyth_user,
            need_funding_workflow=True,
            separate_allocation_requests=False
        )

    @tag("fund_wf")
    def test_bangor_user_sees_funding_workflow_NO(self):
        self._check_funding_workflow(
            self.bangor_user,
            need_funding_workflow=False,
            separate_allocation_requests=False
        )

    @tag("fund_wf")
    def test_cardiff_user_sees_funding_workflow_NO(self):
        self._check_funding_workflow(
            self.cardiff_user,
            need_funding_workflow=False,
            separate_allocation_requests=False
        )

    @tag("fund_wf")
    def test_swansea_user_sees_funding_workflow_YES(self):
        self._check_funding_workflow(
            self.swansea_user,
            need_funding_workflow=True,
            separate_allocation_requests=True
        )

    # RSE requests
    def _check_rse_request_availability(
        self, user, allows_rse_requests, separate_allocation_requests
    ):
        self.sign_in(user)
        self._go_to_project_list_from_dashboard()
        self._select_or_create_fake_project_in_project_list(
            separate_allocation_requests, project_owner=user
        )

        try:
            # TODO: use regexp instead?
            strtofind = "Request RSE support"
            el = self.selenium.find_element_by_link_text(strtofind)
            if not allows_rse_requests:
                raise AssertionError(
                    f'A "{strtofind}" link should not be present'
                )
        except NoSuchElementException:
            if allows_rse_requests:
                raise AssertionError(f'A "{strtofind}" link should be present')

    @tag("RSE_reqs")
    def test_aberystwyth_user_sees_rse_requests_NO(self):
        self._check_rse_request_availability(
            self.aberystwyth_user,
            allows_rse_requests=False,
            separate_allocation_requests=False
        )

    @tag("RSE_reqs")
    def test_bangor_user_sees_rse_requests_NO(self):
        self._check_rse_request_availability(
            self.bangor_user,
            allows_rse_requests=False,
            separate_allocation_requests=False
        )

    @tag("RSE_reqs")
    def test_cardiff_user_sees_rse_requests_NO(self):
        self._check_rse_request_availability(
            self.cardiff_user,
            allows_rse_requests=False,
            separate_allocation_requests=False
        )

    @tag("RSE_reqs")
    def test_swansea_user_sees_rse_requests_YES(self):
        self._check_rse_request_availability(
            self.swansea_user,
            allows_rse_requests=True,
            separate_allocation_requests=True
        )

    # funding approval
    def _check_funding_approval_availability(
        self, user, needs_funding_approval
    ):
        self.sign_in(user)
        # maybe use partial link text or regexp?
        # or some other string reference? This would be much more robust.
        # click on the Attributions link
        self.selenium.find_element_by_link_text('Attributions').click()
        # click on the 'Add' button, which shows a dropdown
        self.selenium.find_element_by_id('add_attribution_dropdown').click()
        # click on the link with text 'Funding Source' in the dropdown
        self.selenium.find_element_by_partial_link_text('Funding Source'
                                                       ).click()
        # brittl1e. Hope the identifier does not change!
        fields = {'id_identifier': self.local_institutional_identifier}
        self.fill_form_by_id(fields)
        # click on the 'Save' button
        self.selenium.find_element_by_css_selector('button.btn.btn-primary'
                                                  ).click()

        # filling the fields that need to be filled
        fields = {'id_title': 'A funding source title', 'id_amount': '1'}
        approver_field_id = 'id_pi_email'
        try:
            el = self.selenium.find_element_by_id(approver_field_id)
            if not needs_funding_approval:
                raise AssertionError('An approver field should not be present')
        except NoSuchElementException:
            if not needs_funding_approval:
                raise AssertionError('An approver field is needed')

        fields[approver_field_id] = 'pi@aber.ac.uk'
        self.fill_form_by_id(fields)
        # taking care of the dropdown
        self.select_from_dropdown_by_id(id='id_funding_body', index=1)

        # click on the 'Save' button
        self.selenium.find_element_by_css_selector('button.btn.btn-primary'
                                                  ).click()

    @tag("funding_approval")
    def test_aberystwyth_user_sees_funding_approval_YES(self):
        self._check_funding_approval_availability(
            user=self.aberystwyth_user, needs_funding_approval=True
        )

    @skipIf(
        True, 'Bangor users do not need funding workflow in the first place.'
    )
    @tag("funding_approval")
    def test_bangor_user_sees_funding_approval_NO(self):
        pass

    @skipIf(
        True, 'Cardiff users do not need funding workflow in the first place'
    )
    @tag("funding_approval")
    def test_cardiff_user_sees_funding_approval_NO(self):
        pass

    @tag("funding_approval")
    def test_swansea_user_sees_funding_approval_YES(self):
        self._check_funding_approval_availability(
            user=self.swansea_user, needs_funding_approval=True
        )

    # supervisor approval
    def _check_supervisor_approval_workflow(
        self, user, needs_supervisor_approval, separate_allocation_requests
    ):
        with patch('project.views.email_user') as mocked_function:
            self.sign_in(user)
            self._create_fake_project_via_ui(
                separate_allocation_requests, project_owner=user
            )
            if needs_supervisor_approval:
                mocked_function.assert_called_once()
            else:
                mocked_function.assert_not_called()

    @tag('supervisor_approval')
    def test_aberystwyth_user_supervisor_approval_workflow_YES(self):
        self._check_supervisor_approval_workflow(
            user=self.aberystwyth_user,
            needs_supervisor_approval=True,
            separate_allocation_requests=False
        )

    @skipIf(True, 'debug')
    @tag('supervisor_approval')
    def test_bangor_user_supervisor_approval_workflow_NO(self):
        self._check_supervisor_approval_workflow(
            user=self.bangor_user,
            needs_supervisor_approval=False,
            separate_allocation_requests=False
        )

    @skipIf(True, 'debug')
    @tag('supervisor_approval')
    def test_cardiff_user_supervisor_approval_workflow_NO(self):
        self._check_supervisor_approval_workflow(
            user=self.cardiff_user,
            needs_supervisor_approval=False,
            separate_allocation_requests=False
        )

    @tag('supervisor_approval')
    def test_swansea_user_supervisor_approval_workflow_YES(self):
        self._check_supervisor_approval_workflow(
            user=self.swansea_user,
            needs_supervisor_approval=True,
            separate_allocation_requests=True
        )

    # user approval
    def _check_user_approval_in_dashboard(
        self, unapproved_user, needs_user_approval
    ):
        # at the dashboard
        self.sign_in(unapproved_user)

        if needs_user_approval:
            # check that user is 'AWAITING APPROVAL'
            match = re.search(
                '[Aa]waiting\s+[Aa]pproval', self.selenium.page_source
            )
            assert match is not None, 'This test must run with an unapproved user.'

        # check that user can/cannot join a project
        match = re.search(
            '[jJ]oin\s+\w*\s+[Pp]roject', self.selenium.page_source
        )
        if needs_user_approval:
            assert match is None, 'Unapproved user cannot join projects'

        # check that user can/cannot access project list
        try:
            el = self.selenium.find_element_by_link_text('Projects')
            if needs_user_approval:
                raise AssertionError(
                    'User awaiting approval should not see the "Projects" link'
                )
        except NoSuchElementException:
            if not needs_user_approval:
                raise AssertionError('User should not see the "Projects" link')

    def _check_user_awaiting_approval_cannot_be_invited_to_project(
        self, project_owner_user, unapproved_user, needs_user_approval
    ):
        self._create_fake_project_approved(project_owner=project_owner_user)
        self.sign_in(project_owner_user)
        self._go_to_project_list_from_dashboard()
        self.selenium.find_element_by_link_text(self.fake_project_title).click()
        self.selenium.find_element_by_link_text('Invite User').click()

        fields = {'email': unapproved_user.email}

        self.fill_form_by_id(fields)
        self.submit_form(fields)

        # compare with /project/forms.py,

        if needs_user_approval:
            assert 'User is still awaiting authorisation' in self.selenium.page_source, 'User awaiting authorisation should not be eligible for invitation'
        else:
            assert 'User is still awaiting authorisation' not in self.selenium.page_source, 'User awaiting authorisation should not matter in invitation'

    @tag('user_approval')
    def test_aberystwyth_user_approval_workflow_dashboard_NO(self):
        self._check_user_approval_in_dashboard(
            unapproved_user=self.aberystwyth_user_aa, needs_user_approval=False
        )

    @tag('user_approval')
    def test_aberystwyth_user_approval_workflow_invitation_NO(self):
        self._check_user_awaiting_approval_cannot_be_invited_to_project(
            project_owner_user=self.aberystwyth_user,
            unapproved_user=self.aberystwyth_user_aa,
            needs_user_approval=False
        )

    @tag('user_approval')
    def test_bangor_user_approval_workflow_dashboard_YES(self):
        self._check_user_approval_in_dashboard(
            unapproved_user=self.bangor_user_aa, needs_user_approval=True
        )

    @tag('user_approval')
    def test_bangor_user_approval_workflow_invitation_YES(self):
        self._check_user_awaiting_approval_cannot_be_invited_to_project(
            project_owner_user=self.bangor_user,
            unapproved_user=self.bangor_user_aa,
            needs_user_approval=True
        )

    @tag('user_approval')
    def test_cardiff_user_approval_workflow_dashboard_YES(self):
        self._check_user_approval_in_dashboard(
            unapproved_user=self.cardiff_user_aa, needs_user_approval=True
        )

    @tag('user_approval')
    def test_cardiff_user_approval_workflow_invitation_YES(self):
        self._check_user_awaiting_approval_cannot_be_invited_to_project(
            project_owner_user=self.cardiff_user,
            unapproved_user=self.cardiff_user_aa,
            needs_user_approval=True
        )

    @tag('user_approval')
    def test_swansea_user_approval_workflow_dashboard_NO(self):
        self._check_user_approval_in_dashboard(
            unapproved_user=self.swansea_user_aa, needs_user_approval=False
        )

    @tag('user_approval')
    def test_swansea_user_approval_workflow_invitation_NO(self):
        self._check_user_awaiting_approval_cannot_be_invited_to_project(
            project_owner_user=self.swansea_user,
            unapproved_user=self.swansea_user_aa,
            needs_user_approval=False
        )
