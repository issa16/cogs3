from django.test import TestCase
from django.urls import reverse

from funding.models import Attribution, FundingBody, FundingSource, Publication
from institution.models import Institution
from users.models import CustomUser


class FundingTests(TestCase):
    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]


class AttributionTests(FundingTests):

    @classmethod
    def create_attribution(cls, title, created_by, owner):
        """
        Create an Attribution instance.

        Args:
            title (): TODO
            created_by (): TODO
            owner (): TODO
        """
        attribution = Attribution.objects.create(
            title=title, created_by=created_by, owner=owner
        )
        return attribution

    def test_attribution_creation(self):
        """
        Ensure we can create an Attribution instance.
        """
        title = 'Attribution title'
        user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        attribution = self.create_attribution(
            title=title, created_by=user, owner=user
        )
        self.assertTrue(isinstance(attribution, Attribution))
        self.assertEqual(attribution.__str__(), title)

    def test_attribution_as_funding_source(self):
        """
        Ensure we can create a FundingSource instance as an Attribution.
        """
        funding_source = FundingSource.objects.get(identifier='scw0002')
        self.assertTrue(funding_source.is_fundingsource)
        self.assertFalse(funding_source.is_publication)

    def test_attribution_as_publication(self):
        """
        Ensure we can create a Publication instance as an Attribution.
        """
        publication = Publication.objects.get(title='Test publication')
        self.assertTrue(publication.is_publication)
        self.assertFalse(publication.is_fundingsource)

    def test_get_funding_sources(self):
        """
        Ensure all funding sources can be queuried via the Attribution class.
        """
        funding_sources = Attribution.objects.get_fundingsources()
        expected_funding_sources = [
            attribution for attribution in Attribution.objects.all()
            if attribution.type == 'fundingsource'
        ]
        self.assertEqual(funding_sources, expected_funding_sources)

    def test_get_publications(self):
        """
        Ensure all publications can be queuried via the Attribution class.
        """
        publications = Attribution.objects.get_publications()
        expected_publications = [
            attribution for attribution in Attribution.objects.all()
            if attribution.type == 'publication'
        ]
        self.assertEqual(publications, expected_publications)

    def test_verbose_type(self):
        """
        Ensure the correct verbose type is returned for attribution types.
        """
        funding_source = Attribution.objects.get_fundingsources()[0]
        self.assertEqual(funding_source.verbose_type, 'Funding Source')

        publication = Attribution.objects.get_publications()[0]
        self.assertEqual(publication.verbose_type, 'Publication')

    def test_child_funding_source_attribution(self):
        attribution = Attribution.objects.get_fundingsources()[0]
        funding_source = FundingSource.objects.get(
            title=attribution.title, owner=attribution.owner
        )
        self.assertEqual(attribution.child, funding_source)

    def test_child_publication_attribution(self):
        attribution = Attribution.objects.get_publications()[0]
        publication = Publication.objects.get(
            title=attribution.title, owner=attribution.owner
        )
        self.assertEqual(attribution.child, publication)

    def test_funding_source_attribution_string_with_user(self):
        funding_source = Attribution.objects.get_fundingsources()[0]
        self.assertEqual(
            funding_source.string(funding_source.owner),
            'Test funding source (awaiting approval)'
        )

    def test_funding_source_attribution_string_without_user(self):
        funding_source = Attribution.objects.get_fundingsources()[0]
        self.assertEqual(funding_source.string(), 'Test funding source')

    def test_publication_attribution_string(self):
        publication = Attribution.objects.get_publications()[0]
        self.assertEqual(publication.string(), 'Test publication')


class FundingBodyTests(FundingTests):

    @classmethod
    def create_funding_body(cls, name, description):
        """
        Create a FundingBody instance.

        Args:
            name (str): Funding body name.
            description (str): Funding body description.
        """
        funding_body = FundingBody.objects.create(
            name=name, description=description
        )
        return funding_body

    def test_funding_body_creation(self):
        """
        Ensure we can create a FundingBody instance.
        """
        name = 'A funding body name'
        description = 'A funding body description'
        funding_body = self.create_funding_body(
            name=name, description=description
        )
        self.assertTrue(isinstance(funding_body, FundingBody))
        self.assertEqual(funding_body.__str__(), funding_body.name)
        self.assertEqual(funding_body.name, name)
        self.assertEqual(funding_body.description, description)


class FundingSourceTests(FundingTests):

    @classmethod
    def create_funding_source(
        cls, title, identifier, funding_body, owner, pi_email, amount
    ):
        """
        Create a FundingSource instance.

        Args:
            title (str): TODO
            identifier (): TODO.
            funding_body (FundingBody): Granting organisation.
            owner (str): TODO
            pi_email (str): TODO
            amount (str): TODO
        """
        funding_source = FundingSource.objects.create(
            title=title,
            identifier=identifier,
            funding_body=funding_body,
            created_by=owner,
            pi_email=pi_email,
            amount=amount,
        )
        return funding_source

    def test_project_funding_source_creation_new_pi(self):
        """
        Ensure we can create a FundingSource instance which generates a new
        user in the database to be its PI.
        """
        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example.ac.uk")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")

        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['new.pi', institution.base_domain])
        num_existing_users = len(CustomUser.objects.all())

        funding_source = self.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )

        self.assertEqual(institution.needs_funding_approval, False)
        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)
        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, user)
        self.assertEqual(len(CustomUser.objects.all()), num_existing_users + 1)

    def test_project_multiple_funding_source_creation_new_pi(self):
        """
        Ensure we can create multiple FundingSource instances when the PI
        is a new user, without that user logging in between creations.
        """
        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example.ac.uk")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")

        title1 = 'A funding source title'
        identifier1 = 'A funding source identifier'
        title2 = 'Another funding source title'
        identifier2 = 'Another funding source identifier'
        pi_email = '@'.join(['new.pi', institution.base_domain])
        num_existing_users = len(CustomUser.objects.all())

        funding_source1 = self.create_funding_source(
            title=title1,
            identifier=identifier1,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )
        funding_source2 = self.create_funding_source(
            title=title2,
            identifier=identifier2,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )

        self.assertEqual(institution.needs_funding_approval, False)
        self.assertTrue(isinstance(funding_source1, FundingSource))
        self.assertEqual(funding_source1.__str__(), funding_source1.title)
        self.assertEqual(funding_source1.title, title1)
        self.assertEqual(funding_source1.identifier, identifier1)
        self.assertEqual(funding_source1.created_by, user)
        self.assertEqual(funding_source1.funding_body, fundingbody)
        self.assertEqual(funding_source1.approved, False)
        self.assertEqual(funding_source1.pi.email, pi_email)
        self.assertEqual(funding_source1.owner, user)

        self.assertTrue(isinstance(funding_source2, FundingSource))
        self.assertEqual(funding_source2.__str__(), funding_source2.title)
        self.assertEqual(funding_source2.title, title2)
        self.assertEqual(funding_source2.identifier, identifier2)
        self.assertEqual(funding_source2.created_by, user)
        self.assertEqual(funding_source2.funding_body, fundingbody)
        self.assertEqual(funding_source2.approved, False)
        self.assertEqual(funding_source2.pi.email, pi_email)
        self.assertEqual(funding_source2.owner, user)

        self.assertEqual(len(CustomUser.objects.all()), num_existing_users + 1)

    def test_project_funding_source_creation_existing_pi(self):
        """
        Ensure we can create a FundingSource instance whose PI is already a
        user.
        """
        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example.ac.uk")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")

        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['shibboleth.user', institution.base_domain])
        num_existing_users = len(CustomUser.objects.all())

        funding_source = self.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )

        self.assertEqual(institution.needs_funding_approval, False)
        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)
        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, user)
        self.assertEqual(len(CustomUser.objects.all()), num_existing_users)

    def test_project_funding_source_creation_with_funding_approval_required(
        self
    ):
        """
        Ensure we can create a FundingSource instance when funding approval is
        required by the institution.
        """
        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example2.ac.uk")
        user = CustomUser.objects.get(email="test.user@example2.ac.uk")

        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['pi', institution.base_domain])

        funding_source = self.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )

        self.assertEqual(institution.needs_funding_approval, True)
        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)
        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, funding_source.pi)

    def test_project_funding_source_creation_new_pi_can_log_in(self):
        """
        Ensure a user created during a FundingSource creation can log in.
        """
        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example.ac.uk")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")

        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['new.pi', institution.base_domain])

        funding_source = self.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=fundingbody,
            owner=user,
            pi_email=pi_email,
            amount=1000,
        )
        headers = {
            'Shib-Identity-Provider':
                (funding_source.pi.profile.institution.identity_provider),
            'REMOTE_USER': pi_email
        }
        response = self.client.get(reverse('login'), **headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete-registration'))


class PublicationTests(FundingTests):

    @classmethod
    def create_publication(cls, title, created_by, owner, url):
        """
        Create a Publication instance.

        Args:
            title (str): Name of publication.
            created_by (CustomUser): Creator of publication.
            owner (CustomUser): Owner of publication.
            url (str): URL of publication. 
        """
        publication = Publication.objects.create(
            title=title, created_by=created_by, owner=owner, url=url
        )
        return publication

    def test_publication_creation(self):
        """
        Ensure we can create a Publication instance.
        """
        title = 'A publication title'
        user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        url = 'https://example.ac.uk/publications/1'
        publication = self.create_publication(
            title=title, created_by=user, owner=user, url=url
        )
        self.assertTrue(isinstance(publication, Publication))
        self.assertEqual(publication.__str__(), title)
        self.assertEqual(publication.title, title)
        self.assertEqual(publication.url, url)
        self.assertEqual(publication.created_by, user)
        self.assertEqual(publication.owner, user)
