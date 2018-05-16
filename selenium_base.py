from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from users.models import CustomUser

webdriver = webdriver.Firefox

class SeleniumTestsBase(StaticLiveServerTestCase):
    fixtures = [ 'institution/fixtures/institutions.yaml', 'project/fixtures/funding_sources.yaml', ]

    serialized_rollback = True

    def get_url(self, url):
        self.selenium.get(self.live_server_url+url)

    def fill_form_by_id(self, fields):
        for field, value in fields.items():
            element = self.selenium.find_element_by_id(field)
            element.send_keys(value)

    def click_by_text(self, text):
        button = self.selenium.find_element_by_xpath("//*[text()='"+text+"']")
        button.click()

    def select_from_dropdown(self, id, index):
        element = Select(self.selenium.find_element_by_id(id))
        element.select_by_index(index)

    def sign_in(self):
        """
        Sign in as a preexisting test user
        """
        # Sign in using the admin page
        self.get_url("/accounts/external/login/")

        form_fields = {
        "id_username": self.user_email,
        "id_password": self.user_password
        }
        self.fill_form_by_id(form_fields)
        self.click_by_text('Login')

    def scroll_bottom(self):
        self.selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    def tearDown(self):
        super(SeleniumTestsBase, self).tearDown()
        self.selenium.quit()

    def setUp(self):
        # Create a user
        self.user_email = "joe@swansea.ac.uk"
        self.user_password = "password"
        self.user = CustomUser(
            username=self.user_email,
            email=self.user_email,
            first_name='Joe',
            last_name='Blogs',
            is_shibboleth_login_required=False,
        )
        self.user.set_password(self.user_password)
        self.user.save()
        self.user.profile.account_status = self.user.profile.APPROVED
        self.user.save()

        # Setup selenium
        self.selenium = webdriver()
        self.selenium.implicitly_wait(10)
