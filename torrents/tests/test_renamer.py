from django.test import TestCase

from unittest.mock import patch

import shows.tests.utils as utils
from torrents import renamer
from torrents.models import Torrent, Download


class TestRenamer(TestCase):

    def tearDown(self):
        renamer.watch_started = False

    @patch('torrents.renamer.threading.Timer')
    @patch('torrents.renamer.check_downloads')
    def test_start_watch(self, check_downloads, timer):
        timer.return_value.daemon = False
        self.assertFalse(renamer.watch_started)
        renamer.start_watch()
        timer.assert_called_with(renamer.INTERVAL, renamer._repeat_watch)
        timer.return_value.start.assert_called_with()
        self.assertTrue(timer.return_value.daemon)
        self.assertEqual(renamer.timer, timer.return_value)
        self.assertFalse(check_downloads.called)
        self.assertTrue(renamer.watch_started)

    @patch('torrents.renamer.threading.Timer')
    @patch('torrents.renamer.check_downloads')
    def test_start_watch_twice(self, check_downloads, timer):
        # starting the watch twice will not cause it to check or schedule
        renamer.start_watch()
        timer.reset_mock()
        renamer.start_watch()
        self.assertFalse(timer.called)
        self.assertTrue(renamer.watch_started)

    @patch('torrents.renamer.threading.Timer')
    @patch('torrents.renamer.check_downloads')
    def test_repeat_watch(self, check_downloads, timer):
        timer.return_value.daemon = False
        renamer.watch_started = True
        renamer._repeat_watch()
        timer.assert_called_with(renamer.INTERVAL, renamer._repeat_watch)
        timer.return_value.start.assert_called_with()
        self.assertTrue(timer.return_value.daemon)
        self.assertEqual(renamer.timer, timer.return_value)
        check_downloads.assert_called_with()
        self.assertTrue(renamer.watch_started)

    @patch('torrents.renamer.threading.Timer')
    def test_cancel_watch(self, timer):
        # test cancelling before starting...
        renamer.cancel_watch()
        self.assertFalse(renamer.watch_started)
        self.assertIsNone(renamer.timer)
        # ...and after
        renamer.start_watch()
        renamer.cancel_watch()
        self.assertFalse(renamer.watch_started)
        self.assertIsNone(renamer.timer)
        timer.return_value.cancel.assert_called_with()

    def make_downloads(self, utorrent_ui):
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

        return download_1, download_2

    @patch('torrents.renamer.threading.Thread')
    @patch('torrents.models.utorrent')
    def test_check_downloads(self, utorrent_ui, thread):
        download_1, download_2 = self.make_downloads(utorrent_ui)
        thread.return_value.daemon = True
        renamer.check_downloads()
        thread.assert_called_once_with(target=renamer.rename_download,
                                       args=(download_1,))
        self.assertFalse(thread.return_value.daemon)
        thread.return_value.start.assert_called_with()

    @patch('torrents.renamer.os.makedirs')
    @patch('torrents.renamer.os.path.exists')
    @patch('torrents.renamer.shutil.copyfile')
    @patch('torrents.models.utorrent')
    def test_rename_download(self, utorrent_ui, copyfile, exists, makedirs):
        utorrent_ui.get_files.return_value = ['~/Downloads/firefly s01e01.mkv']
        exists.return_value = True
        download_1, download_2 = self.make_downloads(utorrent_ui)
        renamer.rename_download(download_1)
        self.assertFalse(makedirs.called)
        copyfile.assert_called_with(
            '~/Downloads/firefly s01e01.mkv',
            '~/Videos/Firefly/Firefly - S01E01 - Serenity.mkv')
        self.assertNotIn(download_1, Download.objects.all())

    @patch('torrents.renamer.os.makedirs')
    @patch('torrents.renamer.os.path.exists')
    @patch('torrents.renamer.shutil.copyfile')
    @patch('torrents.models.utorrent')
    def test_rename_download_make_dir(self, utorrent_ui, copyfile, exists,
                                      makedirs):
        utorrent_ui.get_files.return_value = ['~/Downloads/firefly s01e01.mkv']
        exists.return_value = False
        download_1, download_2 = self.make_downloads(utorrent_ui)
        renamer.rename_download(download_1)
        makedirs.assert_called_with('~/Videos/Firefly')
        copyfile.assert_called_with(
            '~/Downloads/firefly s01e01.mkv',
            '~/Videos/Firefly/Firefly - S01E01 - Serenity.mkv')
