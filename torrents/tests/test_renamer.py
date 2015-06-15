from django.test import TestCase

from unittest.mock import patch

from torrents import renamer
from torrents.models import Torrent, Download


class TestRenamer(TestCase):

    @patch('torrents.renamer.threading.Timer')
    @patch('torrents.renamer.check_downloads')
    def test_start_watch(self, check_downloads, timer):
        renamer.start_watch()
        timer.assert_called_with(renamer.INTERVAL, renamer.start_watch)
        check_downloads.assert_called_with()

    def test_check_downloads(self):
        torrent_1 = Torrent(episode=None, name='torrent 1')
        download_1 = Download(torrent=torrent_1)
        Download.objects.save(download_1)
        torrent_2 = Torrent(episode=None, name='torrent 2')
        download_2 = Download(torrent=torrent_2)
        Download.objects.save(download_2)

        with patch(download_1.status) as status_1:
            with patch(download_2.status) as status_2:
                status_1.return_value.completed = True
                status_2.return_value.completed = False

                renamer.check_downloads()

        # completed downloads should be removed
        self.assertNotIn(download_1, Download.objects.all())
        self.assertIn(download_2, Download.objects.all())
