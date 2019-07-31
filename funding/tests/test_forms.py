from django.test import TestCase

from funding.forms import FundingSourceForm, AddFundingSourceForm
from funding.forms import PublicationForm
from users.models import CustomUser
from funding.models import FundingBody
from institution.models import Institution


class FundingFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]


class FundingSourceFormTests(FundingFormTests, TestCase):

    def test_form_with_invalid_email(self):
        """
        The form should raise ValidationError when given a non-institutional PI email
        """
        funding_body = FundingBody.objects.get(name="Test")
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")
        form = FundingSourceForm(
            user=user,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': funding_body.id,
                'pi_email': 'myemail@gmail.com',
                'amount': 1000,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['pi_email'],
            ['Please enter an institutional email address ending with one of: '
             '@example.ac.uk, @example2.ac.uk, @example3.ac.uk.'],
        )

    def test_form_with_valid_email(self):
        """
        The form should be accepted with an institutional email
        """
        funding_body = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(name="Example University")
        email = '@'.join(['myemail', institution.base_domain])
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")
        form = FundingSourceForm(
            user=user,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': funding_body.id,
                'pi_email': email,
                'amount': 1000,
            },
        )
        self.assertTrue(form.is_valid())

    def test_form_with_user_email(self):
        """
        The form should be accepted with an institutional email
        """
        funding_body = FundingBody.objects.get(name="Test")
        institution = Institution.objects.get(name="Example University")
        email = '@'.join(['myemail', institution.base_domain])
        user = CustomUser.objects.get(email="admin.user@example.ac.uk")
        form = FundingSourceForm(
            user=user,
            data={
                'title': 'Title',
                'identifier': 'Id',
                'funding_body': funding_body.id,
                'pi_email': email,
                'amount': 1000,
            },
        )
        self.assertTrue(form.is_valid())

    def test_add_funding_source_form(self):
        """
        The form only takes an identifier
        """
        form = AddFundingSourceForm(
            data={
                'identifier': 'Id',
            },
        )
        self.assertTrue(form.is_valid())


class PublicationFormTests(FundingFormTests, TestCase):

    def test_form_with_invalid_url(self):
        """
        The form should raise ValidationError when given a URL not from an institutional repository
        """

        user = CustomUser.objects.get(email="shibboleth.user@example.ac.uk")
        form = PublicationForm(
            user=user,
            data={
                'title': 'Title',
                'url': 'https://example.net/my-awexome-publication'
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'],
            ['URL must contain arxiv.org'],
        )
