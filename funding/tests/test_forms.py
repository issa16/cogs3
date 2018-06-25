from django.contrib.auth.models import Group
from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from funding.tests.test_models import FundingBodyTests
from users.tests.test_models import CustomUserTests

from funding.forms import FundingSourceForm


class FundingFormTests(TestCase):

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


class FundingSourceFormTests(FundingFormTests, TestCase):

    def test_form_with_invalid_email(self):
        """
        The form should raise ValidationError when given a non-institutional PI email
        """
        form = FundingSourceForm(
            user = self.owner,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': self.funding_body.id,
                'pi_email': 'myemail@gmail.com',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['pi_email'],
            ['Needs to be a valid institutional email address.'],
        )

    def test_form_with_valid_email(self):
        """
        The form should be accepted with an institutional email
        """
        form = FundingSourceForm(
            user = self.owner,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': self.funding_body.id,
                'pi_email': 'myemail@bangor.ac.uk'
            },
        )
        self.assertTrue(form.is_valid())

    def test_form_with_user_email(self):
        """
        The form should be accepted with an institutional email
        """
        form = FundingSourceForm(
            user = self.owner,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': self.funding_body.id,
                'pi_email': 'owner_email@bangor.ac.uk'
            },
        )
        self.assertTrue(form.is_valid())
