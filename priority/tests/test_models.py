from django.test import TestCase
from django.urls import reverse

from project.models import Project
from funding.models import Attribution, FundingBody, FundingSource, Publication
from institution.models import Institution
from users.models import CustomUser


class PriorityTests(TestCase):
    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]


class Priority_ProjectModelTests(PriorityTests):
    def setUp(self):
        self.project = Project.objects.get(code='scw0000')
        self.publication = Attribution.objects.get(title='Test publication')
        self.fundingsource = self.project.attributions.get().child
        self.tech_lead = self.project.tech_lead
        self.institution = self.tech_lead.profile.institution

    def test_AP_with_no_funding_approval(self):
        self.assertEqual(self.project.AP(), 62000)

    def test_AP_with_unapproved_funding(self):
        self.institution.needs_funding_approval = True
        self.assertEqual(self.project.AP(), 50000)

    def test_AP_with_approved_funding(self):
        self.institution.needs_funding_approval = True
        self.fundingsource.approved = True
        self.fundingsource.amount = 15000
        self.fundingsource.save()
        self.assertEqual(self.project.AP(), 65000)

    def test_AP_with_publication(self):
        self.fundingsource.delete()
        self.project.attributions.add(self.publication)
        self.assertEqual(self.project.AP(), 60000)

    def test_AP_with_publication_and_fundingsource(self):
        self.project.attributions.add(self.publication)
        self.assertEqual(self.project.AP(), 72000)
