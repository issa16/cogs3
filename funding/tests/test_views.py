import json

from django.test import TestCase
from django.urls import reverse

from funding.forms import (AddFundingSourceForm, FundingSourceApprovalForm,
                           FundingSourceForm, PublicationForm)
from funding.models import (FundingBody, FundingSource,
                            FundingSourceMembership, Publication)
from funding.views import (ApproveFundingSource, AttributionDeleteView,
                           AttributionListView, AttributionUpdateView,
                           FundingSourceAddView, FundingSourceCreateView,
                           FundingSourceListView, PublicationCreateView,
                           PublicationListView)
from institution.models import Institution
from project.models import Project
from users.models import CustomUser


class FundingViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'funding/fixtures/tests/funding_source_memberships.json',
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

    def test_fundingsource_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source create view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        user2 = CustomUser.objects.get(email="guest.user@external.ac.uk")
        user3 = CustomUser.objects.get(email="test.user@example2.ac.uk")
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
            {
                'email': user3.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }

            ## funding source endpoint with no identifier
            response = self.client.get(
                reverse('create-funding-source'),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), FundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceCreateView))
            # Check that initial value for identifier form field has not been set
            self.assertEqual(response.context_data.get('form').initial, {})

            ## test funding source endpoint with identifier
            test_identifier = 'my-identifier-for-testing-123$'

            response = self.client.get(
                reverse('create-funding-source-with-identifier', args=[test_identifier]),
                **headers
            )

            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), FundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceCreateView))
            self.assertEqual(response.context_data.get('form').initial['identifier'], test_identifier)
    def test_publication_create_view_without_popup(self):
        """
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")

        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email
        }

        post_data = {
            'title' : 'My publication title',
            'url' : 'https://{}'.format(institution.local_repository_domain)
            }

        url_appends = { '?_popup=1' : 200,
                        '' : 302}

        for url_append, status_code in url_appends.items():
            # Grab publication count
            pub_count = Publication.objects.count()

            # Fire post request
            response = self.client.post(reverse('create-publication')+url_append, data=post_data, **headers)

            # Check that the publication count is incremented with correct data publication
            pub = Publication.objects.last()
            self.assertEqual(pub.title, post_data['title'])
            self.assertEqual(pub.url, post_data['url'])
            self.assertEqual(pub.owner, user)

            # Check that the expected status code is returned
            expected_redirect_url = reverse('list-attributions')
            self.assertEqual(response.status_code, status_code)

            # check redirect URL only for 302
            if status_code == 302:
                self.assertEqual(response.url, expected_redirect_url)

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        # test endpoint with no identifier
        self.access_view_as_unauthorised_user(reverse('create-funding-source'))

        # test endpoint with identifier
        endpoint = reverse('create-funding-source-with-identifier', args=['some-identifier'])
        self.access_view_as_unauthorised_user(endpoint)


class FundingSourceAddViewTests(FundingViewTests, TestCase):
    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
    ]

    # This is overriden this child classes for extension
    url_append_str = ''

    def test_add_fundingsource_view_as_an_authorised_user(self):
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

            # Test get. Response is a form
            response = self.client.get(
                reverse('add-funding-source') + self.url_append_str,
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), AddFundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceAddView))

            # Test post with new id. Redirects to create form
            new_identifier = 'n53c7'
            response = self.client.post(
                reverse('add-funding-source') + self.url_append_str,
                data={
                    'identifier': new_identifier,
                },
                **headers
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/en-gb/funding/create-funding-source/" + new_identifier + self.url_append_str)

    def test_add_fundingsource_view_as_authorised_with_approval_required(self):
        """
        Ensure the correct account types can access the funding source create view.
        """
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(base_domain="example2.ac.uk")
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

            # Test get. Response is a form
            response = self.client.get(
                reverse('add-funding-source') + self.url_append_str,
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), AddFundingSourceForm))
            self.assertTrue(isinstance(response.context_data.get('view'), FundingSourceAddView))

            # Test post with new id. Redirects to create form
            new_identifier = 'n53c7'
            response = self.client.post(
                reverse('add-funding-source') + self.url_append_str,
                data={
                    'identifier': new_identifier
                },
                **headers
            )

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/en-gb/funding/create-funding-source/" + new_identifier + self.url_append_str)

            # Test post with existing id
            existing_identifier = 'scw0001'

            response = self.client.post(
                reverse('add-funding-source') + self.url_append_str,
                data={
                    'identifier': existing_identifier,
                },
                **headers
            )


            if 'popup' in self.url_append_str:
                # when this it not a popup we should return a 302
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "window.close()")
            else:
                # when it is a popup, the popup returns a 200 with the javascript to close the popup
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/en-gb/funding/list/")

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        self.access_view_as_unauthorised_user(reverse('add-funding-source') + self.url_append_str)


class FundingSourceAddViewWithPopupTests(FundingSourceAddViewTests, TestCase):
    url_append_str = '?_popup=1'


class FundingSourceAddViewWithFundingApprovalTests(FundingSourceAddViewTests, TestCase):
    def setUp(self):
        # Set funding approval to true
        institution = Institution.objects.get(name="Example University")
        institution.needs_funding_approval = True
        institution.save()


class FundingSourceAddViewWithUserAsMember(FundingSourceAddViewTests, TestCase):

    def setUp(self):
        # Set funding approval to true
        institution = Institution.objects.get(name="Example University")
        institution.needs_funding_approval = True
        institution.save()

        # fetch test user
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")

        # add user to existing funding source
        existing_identifier = 'scw0001'

        fundingsource = FundingSource.objects.get(identifier=existing_identifier)

        fundingsource_membership = FundingSourceMembership.objects.create(
            fundingsource=fundingsource,
            user=user,
            approved=True)


class AttributionListViewTests(FundingViewTests, TestCase):
    view = AttributionListView
    view_name = 'list-attributions'

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
                reverse(self.view_name),
                **headers
            )
            self.assertEqual(response.status_code,
                             account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'),
                                       self.view))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the attribution list view.
        """
        self.access_view_as_unauthorised_user(reverse(self.view_name))


class ListAttributionsTests(FundingViewTests, TestCase):
    view_name = 'project-list-attributions-with-pk'

    def test_view_with_project_with_attributions(self):
        project_accounts = [
            {
                'user': CustomUser.objects.get(
                    email="shibboleth.user@example.ac.uk"
                ),
                'project': Project.objects.get(pk=1),
                'expected titles': [
                    'Test funding source (awaiting approval)',
                    'Test publication'
                ]
            },
            {
                'user': CustomUser.objects.get(
                    email="test.user@example2.ac.uk"
                ),
                'project': Project.objects.get(pk=2),
                'expected titles': [
                    'Test funding source 2 (awaiting approval)'
                ]
            }
        ]

        for project_account in project_accounts:
            user = project_account['user']
            institution = user.profile.institution
            project = project_account['project']
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': user.email,
            }
            response = self.client.get(
                reverse(self.view_name, args=[project.pk]),
                **headers
            )
            response_content = json.loads(response.content.decode())
            titles = [result['title']
                      for result in response_content['results']]
            for title in project_account['expected titles']:
                self.assertIn(title, titles)
            for title in titles:
                self.assertIn(title, project_account['expected titles'])

    def test_view_with_project_without_attributions_already_attributed(self):
        project_accounts = [
            {
                'user': CustomUser.objects.get(
                    email="shibboleth.user@example.ac.uk"
                ),
                'expected titles': [
                    'Test publication'
                ]
            },
            {
                'user': CustomUser.objects.get(
                    email="test.user@example2.ac.uk"
                ),
                'expected titles': [
                    'Test funding source 2 (awaiting approval)'
                ]
            }
        ]

        for project_account in project_accounts:
            user = project_account['user']
            institution = user.profile.institution
            project = Project.objects.create(
                title='Temporary test project for {}'.format(user.email),
                description='Project description',
                legacy_hpcw_id='HPCW-12345',
                legacy_arcca_id='ARCCA-12345',
                code='scw{}'.format(2000 + user.id),
                institution_reference='BW-12345',
                department='School of Chemistry',
                supervisor_name="Joe Bloggs",
                supervisor_position="RSE",
                supervisor_email="joe.bloggs@swansea.ac.uk",
                tech_lead=user,
            )
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': user.email,
            }
            response = self.client.get(
                reverse(self.view_name, args=[project.pk]),
                **headers
            )
            response_content = json.loads(response.content.decode())
            titles = [result['title']
                      for result in response_content['results']]
            for title in project_account['expected titles']:
                self.assertIn(title, titles)
            for title in titles:
                self.assertIn(title, project_account['expected titles'])


class FundingSourceListViewTests(AttributionListViewTests):
    view = FundingSourceListView
    view_name = 'list-funding_sources'


class PublicationListViewTests(AttributionListViewTests):
    view = PublicationListView
    view_name = 'list-publications'


class FundingSourceUpdateViewTests(FundingViewTests, TestCase):

    def test_fundingource_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        user2 = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(identifier="scw0001")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
            {
                'email': user2.email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            funding_source.pi_email = account.get('email')
            funding_source.save()
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
            self.assertEqual(response.status_code,
                             account.get('expected_status_code'))

            if response.status_code == 200:
                # Allowed to update
                self.assertTrue(isinstance(response.context_data.get('form'),
                                       FundingSourceForm))
                self.assertTrue(isinstance(response.context_data.get('view'),
                                       AttributionUpdateView))

    def test_fundingource_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(base_domain="example2.ac.uk")
        funding_source = FundingSource.objects.get(title="Test funding source 2")

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
            self.assertEqual(response.status_code,
                             account.get('expected_status_code'))

    def test_publication_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the funding source list view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        user2 = CustomUser.objects.get(email="test.user@example2.ac.uk")
        attr_user = CustomUser.objects.get(email="attr.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")
        publication = Publication.objects.get(title="Test publication")

        accounts = [
            {
                'user': user,
                'expected_status_code': 200,
            },
            {
                'user': user2,
                'expected_status_code': 200,
            },
            {
                'user': attr_user,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            # Attr users should always be able to see details
            if account['user'] != attr_user:
                publication.created_by = account.get('user')
                publication.save()
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('user').email,
            }
            response = self.client.get(
                reverse(
                    'update-attribution',
                    args=[publication.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code,
                             account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'),
                                       PublicationForm))
            self.assertTrue(isinstance(response.context_data.get('view'),
                                       AttributionUpdateView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'user': user,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('user').email,
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
                    AttributionDeleteView
                )
            )

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        user2 = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
            {
                'email': user2.email,
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

    def test_view_as_unauthorised_user_with_approved_attribution(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        user2 = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        institution.needs_funding_approval = True
        funding_source = FundingSource.objects.get(title="Test funding source")
        funding_source.approved = True

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
            {
                'email': user2.email,
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
            self.assertEqual(response.status_code,
                             account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-attribution',
                args=[funding_source.id]
            )
        )

    def test_view_without_user_approval(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        funding_source = FundingSource.objects.get(title="Test funding source")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            funding_source.pi_email = account.get('email')
            funding_source.save()
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
            self.assertContains(response, 'Are you sure you want to delete this funding source?')

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-attribution',
                args=[funding_source.id]
            )
        )


class FundingsourceDetailViewTest(FundingViewTests, TestCase):
    def test_view_as_pending_user(self):
        """
        Ensure an unapproved user can not view detail on a funding source.
        """
        fundingsource = FundingSource.objects.get(
            title='Test funding source'
        )
        user = CustomUser.objects.get(email="norman.gordon@example.ac.uk")
        institution = user.profile.institution
        path = reverse('funding_source-detail-view', args=[fundingsource.id])
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email,
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('list-attributions'))

    def test_view_as_owner(self):
        """
        Ensure an unapproved user can not view detail on a funding source.
        """
        fundingsource = FundingSource.objects.get(
            title='Test funding source'
        )
        user = fundingsource.owner
        institution = user.profile.institution
        path = reverse('funding_source-detail-view', args=[fundingsource.id])
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email,
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 200)

    def test_view_as_other_institution_user(self):
        """
        Ensure an unapproved user can not view detail on a funding source.
        """
        fundingsource = FundingSource.objects.get(
            title='Test funding source'
        )
        user = CustomUser.objects.get(email='test.user@example2.ac.uk')
        institution = user.profile.institution
        path = reverse('funding_source-detail-view', args=[fundingsource.id])
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email,
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 200)

    def test_view_as_unrelated_user(self):
        """
        Ensure an unapproved user can not view detail on a funding source.
        """
        fundingsource = FundingSource.objects.get(
            title='Test funding source'
        )
        user = CustomUser.objects.get(email="test.user@example3.ac.uk")
        institution = user.profile.institution
        path = reverse('funding_source-detail-view', args=[fundingsource.id])
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email,
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('list-attributions'))


class ToggleFundingSourceMembershipApprovedTests(FundingViewTests, TestCase):
    def test_view_as_different_users(self):

        funding_source = FundingSource.objects.first()

        # user which is member of funding source
        funding_source_user = CustomUser.objects.get(
            email="test.user@example2.ac.uk"
        )
        membership = FundingSourceMembership.objects.get(
            user=funding_source_user,
            fundingsource=funding_source,
            approved=True
        )

        # double check that this user isn't the funding source pi
        self.assertNotEqual(funding_source.pi.id, funding_source_user.id)

        # user which is pi of (same) funding source
        funding_source_pi = funding_source.pi
        membership2 = FundingSourceMembership.objects.get(
            user=funding_source_pi,
            fundingsource=funding_source,
            approved=True
        )

        # user which isn't member of funding source
        non_funding_source_user = CustomUser.objects.get(
            email="test.user@example2.ac.uk"
        )

        accounts = [
            {
                'email': funding_source_pi.email,
                'expected_status_code': 200,
                'institution': funding_source_pi.profile.institution,
                'membership': membership2,
            }, {
                'email': funding_source_user.email,
                'expected_status_code': 302,
                'institution': funding_source_user.profile.institution,
                'membership': membership,
            }, {
                'email': non_funding_source_user.email,
                'expected_status_code': 302,
                'institution': non_funding_source_user.profile.institution,
                'membership': membership,
            }
        ]

        for account in accounts:
            membership_id = account['membership'].id
            url = reverse('toggle-funding_source_membership-approved',
                          args=[membership_id])

            headers = {
                'Shib-Identity-Provider': (account['institution']
                                           .identity_provider),
                'REMOTE_USER': account['email'],
            }

            response = self.client.get(url, **headers)

            self.assertEqual(response.status_code,
                             account['expected_status_code'])

            # Can't check a huge amount of the content as the form only
            # returns the boolean approved status of the membership
            if response.status_code == 200:
                self.assertContains(response,
                                    'id="id_approved" checked')


class ListUnapprovedFundingSourcesTest(FundingViewTests, TestCase):
    def test_view_as_different_users(self):

        url = reverse('list-unapproved-funding_sources')

        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        admin_user = CustomUser.objects.get(email="admin.user@example.ac.uk")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 403,
            }, {
                'email': admin_user.email,
                'expected_status_code': 200,
            }
        ]

        for account in accounts:
            institution = Institution.objects.get(name="Example University")

            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account['email'],
            }

            response = self.client.get(url, **headers)

            self.assertEqual(response.status_code, account['expected_status_code'])

            # Check that the page at least contains titles for all funding source objects
            if response.status_code == 200:
                [self.assertTrue(f.title in str(response.content.decode())) for f in FundingSource.objects.all()]

class PublicationDeleteViewTests(FundingViewTests, TestCase):

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the delete view.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")

        publication = Publication.objects.get(title="Test publication")

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
                    args=[publication.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(
                isinstance(
                    response.context_data.get('view'),
                    AttributionDeleteView
                )
            )

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="guest.user@external.ac.uk")
        user2 = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        publication = Publication.objects.get(title="Test publication")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
            {
                'email': user2.email,
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
                    args=[publication.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-attribution',
                args=[publication.id]
            )
        )

    def test_view_without_user_approval(self):
        """
        Ensure unauthorised users can not access the delete view.
        """
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")
        institution = Institution.objects.get(name="Example University")
        publication = Publication.objects.get(title="Test publication")

        accounts = [
            {
                'email': user.email,
                'expected_status_code': 302,
            },
        ]
        for account in accounts:
            publication.pi_email = account.get('email')
            publication.save()
            headers = {
                'Shib-Identity-Provider': institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse(
                    'delete-attribution',
                    args=[publication.id]
                ),
                **headers
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))

        self.access_view_as_unauthorised_user(
            reverse(
                'delete-attribution',
                args=[publication.id]
            )
        )


class ListFundingSourceMembershipTests(FundingViewTests, TestCase):
    def test_access_as_unauthorised_user(self):
        """
        Ensure that users not logged in get booted out of this page
        """
        self.access_view_as_unauthorised_user(
            reverse('list-funding_source_memberships')
        )

    def test_access_as_authorised_user(self):
        """
        Check that logged in users can see this page.
        """
        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        institution = Institution.objects.get(name="Example University")
        headers = {
            'Shib-Identity-Provider': institution.identity_provider,
            'REMOTE_USER': user.email,
        }

        response = self.client.get(
            reverse('list-funding_source_memberships'),
            **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test funding source")


class ApproveFundingSourceTests(FundingViewTests, TestCase):

    def setUp(self):
        self.project = Project.objects.get(code='scw0000')

        self.funding_source = FundingSource.objects.create(
            title='A grant for testing with',
            identifier='1234',
            funding_body=FundingBody.objects.get(name='Test'),
            created_by=self.project.tech_lead,
            pi_email='norman.gordon@example.ac.uk',
            amount=1000,
        )

    def test_view_permissions(self):
        accounts = [
            {
                'user': CustomUser.objects.get(
                    email="attr.user@example.ac.uk"
                ),
                'expected_status_code_get': 200,
                'expected_status_code_post': 302,
                'expected_status_code_post_redirect_url': '/en-gb/funding/admin/unapproved_fundingsources/',
                'should_approve' : True
            },
            {
                'user': CustomUser.objects.get(
                    email="shibboleth.user@example.ac.uk"
                ),
                'expected_status_code_get': 403,
                'expected_status_code_post': 403,
                'should_approve' : False
            }
        ]

        for account in accounts:
            headers = {
                'Shib-Identity-Provider': (account.get('user').profile
                                           .institution.identity_provider),
                'REMOTE_USER': account.get('user').email,
            }

            # test viewing the form
            response = self.client.get(
                reverse('approve-funding_source',
                        args=[self.funding_source.id]),
                **headers
            )
            self.assertEqual(response.status_code,
                             account.get('expected_status_code_get'))
            if response.status_code == 200:
                self.assertTrue(isinstance(response.context_data.get('form'),
                                           FundingSourceApprovalForm))
                self.assertTrue(isinstance(response.context_data.get('view'),
                                           ApproveFundingSource))


            # Funding source should not be approved before post self.assertFalse(self.funding_source.approved)
            funding_source = FundingSource.objects.get(id=self.funding_source.id)
            funding_source.approved = False
            funding_source.save()

            self.assertFalse(funding_source.approved)

            # Construct dict
            form_values = {
                'title': 'A grant for testing with',
                'identifier': '1234',
                'amount': 1000,
                'funding_body': 1,
                'pi_email': 'norman.gordon@example.ac.uk',
                'approved': True
            }

            response = self.client.post(
                reverse('approve-funding_source',
                        args=[self.funding_source.id]),
                data=form_values,
                **headers
            )

            self.assertEqual(response.status_code, account['expected_status_code_post'])

            funding_source.refresh_from_db()

            if response.status_code == 302:
                self.assertEqual(response.url, account['expected_status_code_post_redirect_url'])

            if account['should_approve']:
                self.assertTrue(funding_source.approved)
            else:
                self.assertFalse(funding_source.approved)
