from selenium_base import SeleniumTestsBase

class UserIntegrationTests(SeleniumTestsBase):

    def test_external_login(self):
        """
        Sign in as an external user
        """
        #Just sign in. There is an assert in the sign_in function
        for user in [self.user, self.external, self.student, self.rse, self.admin,]:
            self.sign_in(user)
            self.log_out()


    def test_create_user(self):
        """
        Create a new user with an institutional email address
        """
        self.get_url("/accounts/login/?entityID=https://iss-openathensla-runtime.swan.ac.uk/oala/metadata")
        # No shibboleth login in the test case
        assert False
