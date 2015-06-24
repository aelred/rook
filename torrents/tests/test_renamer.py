from django.test import TestCase

from unittest.mock import patch

import shows.tests.utils as utils
from torrents import renamer
from torrents.models import Torrent, Download


class TestRenamer(TestCase):

    @patch('torrents.renamer.threading.Timer')
    @patch('torrents.renamer.check_downloads')
    def test_start_watch(self, check_downloads, timer):
        renamer.start_watch()
        timer.assert_called_with(renamer.INTERVAL, renamer.start_watch)
        check_downloads.assert_called_with()

    @patch('torrents.models.utorrent')
    def test_check_downloads(self, utorrent_ui):
        utorrent_ui.download.return_value = 'my hash'

        episode_1 = utils.episode('Firefly', 1, 1, 'Serenity')
        torrent_1 = Torrent.objects.create(
            episode=episode_1, name='firefly s01e01.mkv', url='f1')
        download_1 = Download.objects.create(torrent=torrent_1)
        download_1.full_clean()

        episode_2 = utils.episode('Firefly', 1, 2, 'The Train Job')
        torrent_2 = Torrent.objects.create(
            episode=episode_2, name='Firefly 01x02 x264 BROWNSHIRTS', url='f2')
        download_2 = Download.objects.create(torrent=torrent_2)
        download_2.full_clean()

        def get_completed(d):
            return {download_1: True, download_2: False}[d]
        utorrent_ui.get_completed = get_completed

        renamer.check_downloads()

        # completed downloads should be removed
        self.assertNotIn(download_1, Download.objects.all())
        self.assertIn(download_2, Download.objects.all())
