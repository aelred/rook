from django.test import TestCase

from settings.config import config, write, read

from unittest.mock import patch, MagicMock


@patch('builtins.open')
class TestConfig(TestCase):

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
