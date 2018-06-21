from django.contrib.auth.models import Group
from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from funding.models import FundingSource
from funding.models import FundingBody
from users.tests.test_models import CustomUserTests


class FundingBodyTests(TestCase):

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

    def test_project_funding_source_creation(self):
        """
        Ensure we can create a FundingBody instance.
        """
        name = 'A function source name'
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

        # Create a funding body
        self.funding_body = FundingBodyTests.create_funding_body(
            name='A function source name',
            description='A funding source description',
        )

    @classmethod
    def create_funding_source(cls, title, identifier, funding_body, owner, pi_email):
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
        )
        return funding_source

    def test_project_funding_source_creation(self):
        """
        Ensure we can create a FundingBody instance.
        """

        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['pi', self.institution.base_domain])
        funding_source = self.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=self.funding_body,
            owner=self.owner,
            pi_email=pi_email,
        )
        self.assertTrue(isinstance(funding_source, FundingSource))
        self.assertEqual(funding_source.__str__(), funding_source.title)
        self.assertEqual(funding_source.title, title)
        self.assertEqual(funding_source.identifier, identifier)
        self.assertEqual(funding_source.created_by, self.owner)
        self.assertEqual(funding_source.funding_body, self.funding_body)
