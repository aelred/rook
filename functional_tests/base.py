from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from rook.test_runner import webdriver


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver()
        self.browser.implicitly_wait(3)
        self.browser.get(self.live_server_url)

    def tearDown(self):
        self.browser.quit()
