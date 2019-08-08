from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

from users.models import CustomUser
from users.notifications import user_created_notification


@override_settings(DEFAULT_SUPPORT_EMAIL='admin_team@example.ac.uk')
class UserCreatedNotificationTests(TestCase):
    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def test_user_created_notification_as_institutional_user(self):
        user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        user_created_notification(user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         f'{settings.COMPANY_NAME} User Account Created')
        self.assertIn('Joe Bloggs', mail.outbox[0].body)
        self.assertIn(user.reason_for_account, mail.outbox[0].body)
