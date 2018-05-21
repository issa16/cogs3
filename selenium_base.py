from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from users.models import CustomUser

from cogs3.settings import SELENIUM_WEBDRIVER


class SeleniumTestsBase(StaticLiveServerTestCase):
    fixtures = [
        'institution/fixtures/institutions.yaml',
        'project/fixtures/funding_sources.yaml',
    ]

    serialized_rollback = True

    def get_url(self, url):
        self.selenium.get(self.live_server_url + url)

    def fill_form_by_id(self, fields):
        for field, value in fields.items():
            element = self.selenium.find_element_by_id(field)
            element.send_keys(value)

    def select_from_dropdown_by_id(self, id, index):
        element = Select(self.selenium.find_element_by_id(id))
        element.select_by_index(index)

    def select_from_first_dropdown(self, index):
        element = Select(self.selenium.find_element_by_xpath("//select[1]"))
        element.select_by_index(index)

    def sign_in(self, user):
        """
        Sign in as a preexisting test user
        """
        # Sign in using the external collaborators login form
        self.get_url("/accounts/external/login/")

        form_fields = {
            "id_username": user.email,
            "id_password": self.user_password,
        }
        self.fill_form_by_id(form_fields)
        self.submit_form(form_fields)
        # Check that we didn't get the fail response
        assert "Please enter a correct email and password" not in  self.selenium.page_source

    def log_out(self):
        self.get_url("/accounts/logout/")
        assert "accounts/logged_out/" in self.selenium.current_url
        self.get_url("")

    def submit_form(self, form_fields):
        key = list(form_fields.keys())[0]
        self.selenium.find_element_by_id(key).send_keys(Keys.RETURN)

    def click_by_id(self, text):
        self.selenium.find_element_by_id(text).click()

    def scroll_bottom(self):
        self.selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def create_test_user(self, user):
        user.set_password(self.user_password)
        user.save()
        user.profile.account_status = user.profile.APPROVED
        user.save()

    def tearDown(self):
        super(SeleniumTestsBase, self).tearDown()
        self.selenium.quit()

    def setUp(self):
        self.user_password = "password"
        self.user = CustomUser(
            username="user@swansea.ac.uk",
            email="user@swansea.ac.uk",
            first_name='User',
            last_name='User',
            is_staff=True,
            is_shibboleth_login_required=False,
        )
        self.create_test_user(self.user)

        self.external = CustomUser(
            username="external@gmail.com",
            email="external@gmail.com",
            first_name='External',
            last_name='External',
            is_shibboleth_login_required=False,
        )
        self.create_test_user(self.user)

        self.student = CustomUser(
            username="123456@swansea.ac.uk",
            email="123456@swansea.ac.uk",
            first_name='Student',
            last_name='Student',
            is_shibboleth_login_required=False,
        )
        self.create_test_user(self.student)

        self.rse = CustomUser(
            username="rse@swansea.ac.uk",
            email="rse@swansea.ac.uk",
            first_name='Rse',
            last_name='Rse',
            is_staff=True,
            is_superuser=True,
            is_shibboleth_login_required=False,
        )
        self.create_test_user(self.rse)

        self.admin = CustomUser(
            username="admin@swansea.ac.uk",
            email="admin@swansea.ac.uk",
            first_name='Admin',
            last_name='Admin',
            is_staff=True,
            is_superuser=True,
            is_shibboleth_login_required=False,
        )
        self.create_test_user(self.admin)

        # Setup selenium
        self.selenium = SELENIUM_WEBDRIVER()
        self.selenium.implicitly_wait(10)
        self.get_url("")
        self.selenium.add_cookie({'name': 'cookielaw_accepted', 'value': '1'})
