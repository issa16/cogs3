import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from django.contrib.auth.models import Group
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate

from cogs3.settings import LANGUAGE_CODE
from cogs3.settings import SELENIUM_WEBDRIVER
from cogs3.settings import SELENIUM_WEBDRIVER_PROFILE
from django.core.exceptions import ObjectDoesNotExist
from institution.models import Institution
from users.models import CustomUser
from funding.models import FundingBody


class SeleniumTestsBase(StaticLiveServerTestCase):
    fixtures = [
        'institution/fixtures/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/funding_sources.json',
    ]

    serialized_rollback = True

    def get_url(self, url):
        self.selenium.get(self.live_server_url + url)

    def click_link_by_url(self, url):
        selector = 'a[href="' + url + '"]'
        link = self.selenium.find_element_by_css_selector(selector)
        link.click()

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
        self.get_url(reverse('external-login'))

        form_fields = {
            "id_username": user.email,
            "id_password": self.user_password,
        }
        self.fill_form_by_id(form_fields)
        self.submit_form(form_fields)
        # Check that we didn't get the fail response
        if "Please enter a correct email and password" in self.selenium.page_source:
            raise AssertionError()

    def log_out(self):
        self.get_url(reverse('logout'))
        if "accounts/logged_out/" not in self.selenium.current_url:
            raise AssertionError()
        self.get_url('')

    def submit_form(self, form_fields):
        key = list(form_fields.keys())[0]
        self.selenium.find_element_by_id(key).send_keys(Keys.RETURN)
        # This seems to be necessary Geckodriver (Firefox)
        # I'm guessing it take a moment to process the submission
        time.sleep(1)

    def click_by_id(self, text):
        self.selenium.find_element_by_id(text).click()

    def scroll_bottom(self):
        self.selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def create_test_user(self, user):
        user.set_password(self.user_password)
        user.save()
        user.profile.account_status = user.profile.APPROVED
        user.save()
        try:
            domain = user.email.split('@')[1]
            institute = Institution.objects.get(base_domain=domain)
            self.user.profile.institution = institute
            self.user.profile.save()
        except ObjectDoesNotExist:
            pass

    def tearDown(self):
        super(SeleniumTestsBase, self).tearDown()
        self.selenium.quit()

    def setUp(self):
        # Create a funding body
        self.funding_body = FundingBody(
            name='A function source name',
            description='A funding source description',
        )
        self.funding_body.save()

        # Create a number of user for different roles
        self.user_password = "password"
        institution = Institution.objects.get(id=1)
        email = '@'.join(['user', institution.base_domain])
        self.user = CustomUser(
            username=email,
            email=email,
            first_name='User',
            last_name='User',
            is_staff=False,
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(self.user)

        # Assign the project owner permission to the user
        project_owner_group = Group.objects.get(name='project_owner')
        self.user.groups.add(project_owner_group)

        self.external = CustomUser(
            username="external@gmail.com",
            email="external@gmail.com",
            first_name='External',
            last_name='External',
            is_shibboleth_login_required=False,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(self.external)

        self.student = CustomUser(
            username="123456@example.ac.uk",
            email="123456@example.ac.uk",
            first_name='Student',
            last_name='Student',
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(self.student)

        self.rse = CustomUser(
            username="rse@example.ac.uk",
            email="rse@example.ac.uk",
            first_name='Rse',
            last_name='Rse',
            is_staff=True,
            is_superuser=True,
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(self.rse)

        self.admin = CustomUser(
            username="admin@example.ac.uk",
            email="admin@example.ac.uk",
            first_name='Admin',
            last_name='Admin',
            is_staff=True,
            is_superuser=True,
            is_shibboleth_login_required=True,
            accepted_terms_and_conditions=True,
        )
        self.create_test_user(self.admin)

        # Setup selenium
        activate(LANGUAGE_CODE)
        profile = SELENIUM_WEBDRIVER_PROFILE()
        profile.set_preference('intl.accept_languages', 'en-gb')
        self.selenium = SELENIUM_WEBDRIVER(profile)
        self.selenium.implicitly_wait(2)
        self.get_url('')
        self.selenium.add_cookie({
            'name': 'cookielaw_accepted',
            'value': '1',
        })
