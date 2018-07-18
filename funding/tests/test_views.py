from django.test import TestCase
from django.urls import reverse

from funding.forms import FundingSourceForm
from funding.views import FundingSourceCreateView
from funding.views import FundingSourceListView
from funding.views import FundingSourceUpdateView
from funding.views import FundingSourceDeleteView
from users.models import CustomUser
from funding.models import FundingSource
from institution.models import Institution


class FundingViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/funding_sources.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def access_view_as_unauthorised_user(self, path):
        """
        Ensure an unauthorised user can not access a particular view.

        Args:
            path (str): Path to view.
        """
        institution = Institution.objects.get(name="Example University")
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
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
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        user2 = CustomUser.objects.get(email="guest.user@external.ac.uk")
        institution = Institution.objects.get(name="Example University")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
            {
                'email': user2.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
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
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        user2 = CustomUser.objects.get(email="guest.user@external.ac.uk")
        institution = Institution.objects.get(name="Example University")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
            {
                'email': user2.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse('list-attributions'),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceListView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        self.access_view_as_unauthorised_user(reverse('list-attributions'))


class FundingSourceUpdateViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'update-attribution',
                    args=[funding_source.id]
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
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'update-attribution',
                    args=[funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'update-attribution',
                args=[funding_source.id]
            )
        )


class FundingSourceDeleteViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the delete view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'delete-attribution',
                    args=[funding_source.id]
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

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'delete-attribution',
                    args=[funding_source.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-attribution',
                args=[funding_source.id]
            )
        )
