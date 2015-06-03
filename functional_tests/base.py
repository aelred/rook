from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import os

from rook.test_runner import webdriver
import settings.config
import rook.startup


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        # delete the config file and replace with default
        os.remove(settings.config.path())
        rook.startup.run()

        self.browser = webdriver()
        self.browser.implicitly_wait(3)
        self.browser.get(self.live_server_url)

    def tearDown(self):
        self.browser.quit()

    def go_to_settings(self):
        self.browser.find_element_by_id('settings').click()

    def choose_settings(self, settings):
        for setting, value in settings.items():
            inputbox = self.browser.find_element_by_id(setting)
            inputbox.clear()
            inputbox.send_keys(value)

        self.browser.find_element_by_id('apply').click()
