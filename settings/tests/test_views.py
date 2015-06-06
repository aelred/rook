from django.test import TestCase

from unittest.mock import patch
import shutil
import os
import urllib.error

import settings.config
import rook.startup


@patch('settings.views.utorrent_ui')
class TestSettingsView(TestCase):

    test_config = {
        'utorrent': {
            'host': '127.0.0.1:8416',
            'username': 'frodo',
            'password': 'mellon'
        }
    }

    def setUp(self):
        # delete config folder like it's a fresh startup
        shutil.rmtree(settings.config.DIR)
        rook.startup.run()

    def test_settings_view(self, utorrent_ui):
        response = self.client.get('/settings')
        self.assertTemplateUsed(response, 'settings.html')

    def test_write_default(self, utorrent_ui):
        with open(settings.config.path()) as f:
            config = f.readlines()
        self.assertIn('[utorrent]\n', config)
        self.assertIn('host = localhost:8080\n', config)
        self.assertIn('username = admin\n', config)
        self.assertIn('password = \n', config)

    def test_read_settings(self, utorrent_ui):
        # create a settings file
        if not os.path.exists(settings.config.DIR):
            os.makedirs(settings.config.DIR)

        with open(settings.config.path(), 'w+') as f:
            f.write('[utorrent]\n')
            f.write('host = thehost:1\n')
            f.write('username = myusername\n')
            f.write('password = pass\n')

        # simulate starting up
        rook.startup.run()

        response = self.client.get('/settings')
        self.assertEqual(response.context['utorrent_host'], 'thehost:1')
        self.assertEqual(response.context['utorrent_username'], 'myusername')
        self.assertEqual(response.context['utorrent_password'], 'pass')

    @patch.dict('settings.config.config', test_config)
    def test_utorrent_settings(self, utorrent_ui):
        response = self.client.get('/settings')
        ut_config = self.test_config['utorrent']
        self.assertEqual(response.context['utorrent_host'], ut_config['host'])
        self.assertEqual(response.context['utorrent_username'],
                         ut_config['username'])
        self.assertEqual(response.context['utorrent_password'],
                         ut_config['password'])

        # test setting parameters
        self.client.post('/settings', data={'utorrent-host': 'new'})
        utorrent_ui.set_params.assert_called_with(
            host='new', username=ut_config['username'],
            password=ut_config['password']
        )

    def test_changing_settings(self, utorrent_ui):
        data = {
            'csrfmiddlewaretoken': 'blahblahblah',
            'utorrent-username': 'bilbo',
            'utorrent-password': 'secret'
        }
        post_response = self.client.post('/settings', data=data)
        self.assertRedirects(post_response, '/settings')
        response = self.client.get('/settings')
        self.assertEquals(response.context['utorrent_username'], 'bilbo')
        self.assertEquals(response.context['utorrent_password'], 'secret')

    def test_saving_settings(self, utorrent_ui):
        data = {'utorrent-host': 'localhost:9000'}
        self.client.post('/settings', data=data)

        with open(settings.config.path()) as f:
            config = f.read()
        self.assertIn('host = localhost:9000', config)

    def test_invalid_utorrent_host(self, utorrent_ui):
        utorrent_ui.set_params.side_effect = urllib.error.URLError(None)
        response = self.client.post('/settings', {'utorrent-host': 'whatev'})
        self.assertIn('uTorrent connection failed', response.context['error'])

    def test_invalid_utorrent_auth(self, utorrent_ui):
        utorrent_ui.set_params.side_effect = urllib.error.HTTPError(
            None, None, None, None, None
        )
        response = self.client.post('/settings', {'utorrent-host': 'whatev'})
        self.assertIn('uTorrent authorization failed',
                      response.context['error'])
