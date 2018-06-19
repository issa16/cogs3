from selenium_base import SeleniumTestsBase
from django.urls import reverse

from users.models import CustomUser


class UserIntegrationTests(SeleniumTestsBase):

    def test_user_login(self):
        """
        Sign in as an external user
        """
        # Just sign in. There is an assert in the sign_in function
        users = [
            self.user,
            self.external,
            self.student,
            self.rse,
            self.admin,
        ]
        for user in users:
            self.sign_in(user)
            self.log_out()

    def test_user_update_info(self):
        """
        Update user information
        """
        self.sign_in(self.user)
        self.click_link_by_url(reverse('update-user'))
        self.fill_form_by_id({
            'id_first_name': 'John',
            'id_last_name': 'Doe'
        })
        self.submit_form({'id_first_name': 'Test'})

        user = CustomUser.objects.get(id=self.user.id)
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
