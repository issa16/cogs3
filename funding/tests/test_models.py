from django.test import TestCase

from funding.models import FundingSource
from funding.models import FundingBody
from institution.models import Institution
from users.models import CustomUser


class FundingBodyTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    @classmethod
    def create_funding_body(cls, name, description):
        """
        Create a FundingBody instance.

        Args:
            name (str): Funding source name.
            description (str): Funding source description.
        """
        funding_body = FundingBody.objects.create(
            name=name,
            description=description,
        )
        return funding_body

    def test_funding_body_creation(self):
        """
        Ensure we can create a FundingBody instance.
        """
        name = 'A funding source name'
        description = 'A funding source description'
        funding_body = self.create_funding_body(
            name=name,
            description=description,
        )
        self.assertTrue(isinstance(funding_body, FundingBody))
        self.assertEqual(funding_body.__str__(), funding_body.name)
        self.assertEqual(funding_body.name, name)
        self.assertEqual(funding_body.description, description)


class FundingSourceTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    @classmethod
    def create_funding_source(cls, title, identifier, funding_body, owner, pi_email, amount):
        """
        Create a FundingSource instance.

        Args:
            title (str): Funding source name.
            description (str): Funding source description.
            fundingbody (FundingBody): Granting organisation
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

    def test_project_funding_source_creation(self):
        """
        Ensure we can create a FundingBody instance.
        """

        fundingbody = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(base_domain="example.ac.uk")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")

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

        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)
        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, user)

    def test_project_funding_source_creation_with_approval_required(self):
        """
        Ensure we can create a Fundingsource instance when approval is
        required by the institution
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

        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)

        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, user)

    def test_project_funding_source_creation_with_approval_required(self):
        """
        Ensure we can create a Fundingsource instance when approval is
        required by the institution
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
        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, user)
        self.assertEqual(funding_source.funding_body, fundingbody)

        self.assertEqual(funding_source.approved, False)
        self.assertEqual(funding_source.pi.email, pi_email)
        self.assertEqual(funding_source.owner, funding_source.pi)
