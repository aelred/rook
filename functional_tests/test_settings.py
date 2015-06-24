from .base import FunctionalTest

from unittest.mock import patch, MagicMock
import urllib.error


class SettingsTest(FunctionalTest):

    def check_setting(self, setting, value, label=None, password=False):
        inputbox = self.browser.find_element_by_id(setting)
        self.assertEqual(inputbox.get_attribute('value'), value)

        if label is not None:
            label_elem = self.browser.find_element_by_id(
                '{}-label'.format(setting))
            self.assertEqual(label_elem.text, label)

        if password:
            self.assertEquals(inputbox.get_attribute('type'), 'password')

    def check_no_errors(self):
        errors = self.browser.find_elements_by_id('error-text')
        self.assertTrue(len(errors) == 0)

    def test_default_settings(self):
        self.go_to_settings()

        self.check_setting('general-videos', '~/Videos', 'Videos directory')
        self.check_setting('utorrent-host', 'localhost:8080', 'uTorrent host')
        self.check_setting('utorrent-username', 'admin', 'uTorrent username')
        self.check_setting('utorrent-password', '', 'uTorrent password',
                           password=True)

    @patch('torrents.utorrent_ui.client')
    def test_save_settings(self, ut_client):
        self.go_to_settings()

        # set some valid settings
        self.choose_settings({
            'utorrent-host': '127.0.0.1:3241',
            'utorrent-username': 'me',
            'utorrent-password': 'that',
        })

        # check settings are applied
        self.check_setting('utorrent-host', '127.0.0.1:3241')
        self.check_setting('utorrent-username', 'me')
        self.check_setting('utorrent-password', 'that')

        self.check_no_errors()

    @patch('torrents.utorrent_ui.client')
    def test_invalid_utorrent_settings(self, ut_client):

        # set up mock uTorrent web UI login
        def ut_cons(host, username, password, timeout):
            if host != 'http://192.168.0.240:1234/gui/':
                raise urllib.error.URLError(None)
            if username != 'admin' or password != 'secret':
                raise urllib.error.HTTPError(None, None, None, None, None)
            return MagicMock()

        ut_client.UTorrentClient = ut_cons

        self.go_to_settings()

        # make sure errors appear when settings are invalid
        self.choose_settings({'utorrent-host': '192.168.0.230:1234'})
        error = self.browser.find_element_by_id('error-text').text
        self.assertEquals('uTorrent connection failed. '
                          'Please check the uTorrent host is correct.', error)

        # make sure the host is still set, despite being incorrect
        self.check_setting('utorrent-host', '192.168.0.230:1234')

        self.choose_settings({'utorrent-host': '192.168.0.240:1234'})
        error = self.browser.find_element_by_id('error-text').text
        self.assertEquals('uTorrent authorization failed. Please check the '
                          'uTorrent username and password is correct.', error)

        self.choose_settings({'utorrent-password': 'secret'})

        # make sure errors vanish once settings are valid
        self.check_no_errors()

        # make sure settings have been applied
        self.check_setting('utorrent-host', '192.168.0.240:1234')
        self.check_setting('utorrent-password', 'secret')
