from django.test import TestCase

from settings.config import config, write, read, update, videos_path

from unittest.mock import patch, MagicMock


@patch('settings.config.utorrent_ui')
@patch('builtins.open')
class TestConfig(TestCase):

    @patch('settings.config.config.read_file')
    def test_read(self, read_func, open_func, utorrent_ui):
        open_func.return_value = MagicMock()
        enter = open_func.return_value.__enter__.return_value
        self.assertFalse(read_func.called)
        read()
        read_func.assert_called_with(enter)

    @patch('settings.config.update')
    def test_read_calls_update(self, update, open_func, utorrent_ui):
        read()
        update.assert_called_once_with()

    @patch('settings.config.config.write')
    def test_write(self, write_func, open_func, utorrent_ui):
        open_func.return_value = MagicMock()
        enter = open_func.return_value.__enter__.return_value
        self.assertFalse(write_func.called)
        write()
        write_func.assert_called_with(enter)

    @patch('settings.config.update')
    def test_write_calls_update(self, update, open_func, utorrent_ui):
        write()
        update.assert_called_once_with()

    def test_defaults(self, open_func, utorrent_ui):
        self.assertEqual(config['utorrent']['host'], 'localhost:8080')
        self.assertEqual(config['utorrent']['username'], 'admin')
        self.assertEqual(config['utorrent']['password'], '')

    def test_update(self, open_func, utorrent_ui):
        update()
        utorrent_ui.set_params.assert_called_once_with(**config['utorrent'])

    @patch('settings.config.os.path.expanduser')
    def test_videos_path(self, expanduser, open_func, utorrent_ui):
        self.assertEqual(videos_path(), expanduser.return_value)
        expanduser.assert_called_once_with('~/Videos')
