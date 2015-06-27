from django.test import TestCase

from unittest.mock import patch

import rook.startup


class TestStartup(TestCase):

    @patch('rook.startup.settings.config.read')
    @patch('rook.startup.torrents.renamer.start_watch')
    @patch('rook.startup.Show.objects.start_update_thread')
    def test_run(self, start_update_thread, start_watch, read_func):
        rook.startup.run()
        read_func.assert_called_once_with()
        start_watch.assert_called_once_with()
        start_update_thread.assert_called_once_with()
