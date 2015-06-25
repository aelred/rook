from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import os
import tempfile
import shutil

from rook.test_runner import webdriver
import settings.config
import rook.startup
import torrents.renamer


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        # delete the config file and replace with default
        os.remove(settings.config.path())
        rook.startup.run()

        # create a directory for torrents to download to and for videos
        self.torrents_dir = tempfile.mkdtemp()
        self.videos_dir = tempfile.mkdtemp()

        self.browser = webdriver()
        self.browser.implicitly_wait(3)
        self.browser.get(self.live_server_url)

        # make sure renamer is running with faster settings
        torrents.renamer.cancel_watch()
        torrents.renamer.start_watch()

    def tearDown(self):
        # delete temp directories
        shutil.rmtree(self.torrents_dir)
        shutil.rmtree(self.videos_dir)

        self.browser.quit()

    def go_to_settings(self):
        self.browser.find_element_by_id('settings').click()

    def choose_settings(self, settings):
        for setting, value in settings.items():
            inputbox = self.browser.find_element_by_id(setting)
            inputbox.clear()
            inputbox.send_keys(value)

        self.browser.find_element_by_id('apply').click()
