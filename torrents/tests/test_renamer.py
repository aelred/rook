from django.test import TestCase

from unittest.mock import patch

import shows.tests.utils as utils
from torrents import renamer
from torrents.models import Torrent, Download


class TestRenamer(TestCase):

    def make_downloads(self):
        self.utorrent.download.return_value = 'my hash'

        episode_1 = utils.episode('Firefly', 1, 1, 'Serenity')
        torrent_1 = Torrent.objects.create(
            episode=episode_1, name='firefly s01e01.mkv', url='f1')
        self.download_1 = Download.objects.create(torrent=torrent_1)
        self.download_1.full_clean()

        episode_2 = utils.episode('Firefly', 1, 2, 'The Train Job')
        torrent_2 = Torrent.objects.create(
            episode=episode_2, name='Firefly 01x02 x264 BROWNSHIRTS', url='f2')
        self.download_2 = Download.objects.create(torrent=torrent_2)
        self.download_2.full_clean()

        def get_completed(d):
            return {self.download_1: True, self.download_2: False}[d]
        self.utorrent.get_completed = get_completed

        def get_files(d):
            return {
                self.download_1: ['~/Downloads/firefly s01e01.mkv'],
                self.download_2: ['~/Downloads/ff0102.mp4']
            }[d]
        self.utorrent.get_files = get_files

    def setUp(self):
        self.addCleanup(patch.stopall)
        self.timer = patch('torrents.renamer.threading.Timer').start()
        self.utorrent = patch('torrents.models.utorrent').start()
        self.makedirs = patch('torrents.renamer.os.makedirs').start()
        self.copyfile = patch('torrents.renamer.shutil.copyfile').start()
        self.path_exists = patch('torrents.renamer.os.path.exists').start()
        self.make_downloads()

    def tearDown(self):
        renamer.watch_started = False

    @patch('torrents.renamer.check_downloads')
    def test_start_watch(self, check_downloads):
        self.timer.return_value.daemon = False
        self.assertFalse(renamer.watch_started)
        renamer.start_watch()
        self.timer.assert_called_with(renamer.INTERVAL, renamer._repeat_watch)
        self.timer.return_value.start.assert_called_with()
        self.assertTrue(self.timer.return_value.daemon)
        self.assertEqual(renamer.timer, self.timer.return_value)
        self.assertFalse(check_downloads.called)
        self.assertTrue(renamer.watch_started)

    @patch('torrents.renamer.check_downloads')
    def test_start_watch_twice(self, check_downloads):
        # starting the watch twice will not cause it to check or schedule
        renamer.start_watch()
        self.timer.reset_mock()
        renamer.start_watch()
        self.assertFalse(self.timer.called)
        self.assertTrue(renamer.watch_started)

    @patch('torrents.renamer.check_downloads')
    def test_repeat_watch(self, check_downloads):
        self.timer.return_value.daemon = False
        renamer.watch_started = True
        renamer._repeat_watch()
        self.timer.assert_called_with(renamer.INTERVAL, renamer._repeat_watch)
        self.timer.return_value.start.assert_called_with()
        self.assertTrue(self.timer.return_value.daemon)
        self.assertEqual(renamer.timer, self.timer.return_value)
        check_downloads.assert_called_with()
        self.assertTrue(renamer.watch_started)

    def test_cancel_watch(self):
        # test cancelling before starting...
        renamer.cancel_watch()
        self.assertFalse(renamer.watch_started)
        self.assertIsNone(renamer.timer)
        # ...and after
        renamer.start_watch()
        renamer.cancel_watch()
        self.assertFalse(renamer.watch_started)
        self.assertIsNone(renamer.timer)
        self.timer.return_value.cancel.assert_called_with()

    @patch('torrents.renamer.threading.Thread')
    def test_check_downloads(self, thread):
        thread.return_value.daemon = True
        renamer.check_downloads()
        thread.assert_called_once_with(target=renamer.rename_download,
                                       args=(self.download_1,))
        self.assertFalse(thread.return_value.daemon)
        thread.return_value.start.assert_called_with()

    def test_rename_download(self):
        self.path_exists.return_value = True
        renamer.rename_download(self.download_1)
        self.assertFalse(self.makedirs.called)
        self.copyfile.assert_called_with(
            '~/Downloads/firefly s01e01.mkv',
            '~/Videos/Firefly/Firefly - S01E01 - Serenity.mkv')
        self.assertNotIn(self.download_1, Download.objects.all())

    def test_rename_download_make_dir(self):
        self.path_exists.return_value = False
        renamer.rename_download(self.download_1)
        self.makedirs.assert_called_with('~/Videos/Firefly')
        self.copyfile.assert_called_with(
            '~/Downloads/firefly s01e01.mkv',
            '~/Videos/Firefly/Firefly - S01E01 - Serenity.mkv')
