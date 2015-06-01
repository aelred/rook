from django.test import TestCase

from settings.config import config, write, read
import rook.startup

from unittest.mock import patch, MagicMock


@patch('settings.config.write')
@patch('settings.views.utorrent_ui')
class TestSettingsView(TestCase):

    test_config = {
        'utorrent': {
            'host': '127.0.0.1:8416',
            'username': 'frodo',
            'password': 'mellon'
        }
    }

    def tearDown(self):
        # reset config file
        rook.startup.run()

    def test_settings_view(self, utorrent_ui, write_func):
        response = self.client.get('/settings')
        self.assertTemplateUsed(response, 'settings.html')

    @patch.dict('settings.config.config', test_config)
    def test_utorrent_settings(self, utorrent_ui, write_func):
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

    def test_changing_settings(self, utorrent_ui, write_func):
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

    def test_saving_settings(self, utorrent_ui, write_func):
        data = {'utorrent-host': 'localhost:9000'}
        self.assertFalse(write_func.called)
        self.client.post('/settings', data=data)
        self.assertTrue(write_func.called)


@patch('builtins.open')
class TestConfig(TestCase):

    def tearDown(self):
        # reset config file
        rook.startup.run()

    @patch('settings.config.config.read')
    def test_read(self, read_func, open_func):
        open_func.return_value = MagicMock()
        enter = open_func.return_value.__enter__.return_value
        self.assertFalse(read_func.called)
        read()
        read_func.assert_called_with(enter)

    @patch('settings.config.config.write')
    def test_write(self, write_func, open_func):
        open_func.return_value = MagicMock()
        enter = open_func.return_value.__enter__.return_value
        self.assertFalse(write_func.called)
        write()
        write_func.assert_called_with(enter)

    def test_defaults(self, open_func):
        self.assertEqual(config['utorrent']['host'], 'localhost:8080')
        self.assertEqual(config['utorrent']['username'], 'admin')
        self.assertEqual(config['utorrent']['password'], '')
