from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from funding.forms import FundingSourceForm
from funding.views import FundingSourceCreateView
from funding.views import FundingSourceListView
from funding.views import FundingSourceUpdateView
from funding.views import FundingSourceDeleteView

from institution.tests.test_models import InstitutionTests
from funding.tests.test_models import FundingSourceTests
from funding.tests.test_models import FundingBodyTests
from users.tests.test_models import CustomUserTests


class FundingViewTests(TestCase):

    def setUp(self):
        # Create an institution for owner
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
            identity_provider='https://idp.bangor.ac.uk/shibboleth',
        )

        # Create the owner
        group = Group.objects.get(name='project_owner')
        self.owner_email = '@'.join(['project_owner', self.institution.base_domain])
        self.owner = CustomUserTests.create_custom_user(
            email=self.owner_email,
            group=group,
        )

        # Create a second user
        self.other_user_email = '@'.join(['other_user', self.institution.base_domain])
        self.other_user = CustomUserTests.create_custom_user(
            email=self.other_user_email,
            group=group,
        )


        # Create a funding body
        self.funding_body = FundingBodyTests.create_funding_body(
            name='A funding source name',
            description='A funding source description',
        )

        # Create a funding source
        self.funding_source = FundingSourceTests.create_funding_source(
            title='title',
            identifier='identifier',
            funding_body=self.funding_body,
            owner=self.owner,
            pi_email='@'.join(['pi', self.institution.base_domain]),
        )

    def access_view_as_unauthorised_user(self, path):
        """
        Ensure an unauthorised user can not access a particular view.

        Args:
            path (str): Path to view.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': 'invalid-remote-user',
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))


class FundingSourceCreateViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source create view.
        """
        accounts = [
            {
                'email': self.owner_email,
                'expected_status_code': 200,
            },
            {
                'email': self.other_user_email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse('create-funding-source'),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), FundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceCreateView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        self.access_view_as_unauthorised_user(reverse('create-funding-source'))


class FundingSourceListViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        accounts = [
            {
                'email': self.owner_email,
                'expected_status_code': 200,
            },
            {
                'email': self.other_user_email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse('list-funding-sources'),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceListView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        self.access_view_as_unauthorised_user(reverse('list-funding-sources'))


class FundingSourceUpdateViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        accounts = [
            {
                'email': self.owner_email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'funding-source-update',
                    args=[self.funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), FundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceUpdateView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        accounts = [
            {
                'email': self.other_user_email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'funding-source-update',
                    args=[self.funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'funding-source-update',
                args=[self.funding_source.id]
            )
        )


class FundingSourceDeleteViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        accounts = [
            {
                'email': self.owner_email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'delete-funding-source',
                    args=[self.funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(
                isinstance(
                    response.context_data.get('view'),
                    FundingSourceDeleteView
                )
            )

    def test_view_as_an_inauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        accounts = [
            {
                'email': self.other_user_email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'delete-funding-source',
                    args=[self.funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-funding-source',
                args=[self.funding_source.id]
            )
        )
