from django.test import TestCase

from unittest.mock import patch

import rook.startup


class TestStartup(TestCase):

    @patch('rook.startup.settings.config.read')
    def test_run(self, read_func):
        rook.startup.run()
        read_func.assert_called_once_with()
