from django.test import TestCase
from django.core.exceptions import ValidationError

import itertools
from unittest.mock import patch

from shows.models import Show, Season, Episode
from torrents.models import Torrent, Download


class TorrentModelTest(TestCase):

    def setUp(self):
        show = Show.objects.create(title='Breaking Bad')
        season = Season.objects.create(show=show, num=3)
        self.episode_1 = Episode.objects.create(season=season, num=2)
        self.episode_2 = Episode.objects.create(season=season, num=3)

    def test_find_all(self):
        # test searching for torrents
        torrents = Torrent.find_all(self.episode_1)

        has_torrents = False
        for torrent in itertools.islice(torrents, 10):
            has_torrents = True
            torrent.clean()
            self.assertEquals(torrent.episode, self.episode_1)
            self.assertIn('breaking bad',
                          torrent.name.lower().replace('.', ' '))
            self.assertIn('3', torrent.name)
            self.assertIn('2', torrent.name)

        self.assertTrue(has_torrents)

    def test_unique(self):
        # Test good state
        torrent_1 = Torrent.objects.create(episode=self.episode_1, name='a',
                                           url='0')
        torrent_2 = Torrent.objects.create(episode=self.episode_1, name='a',
                                           url='1')
        torrent_1.full_clean()
        torrent_2.full_clean()

        # Test bad state
        with self.assertRaises(ValidationError):
            Torrent(episode=self.episode_2, name='a', url='0').full_clean()


@patch('torrents.models.utorrent')
class DownloadModelTest(TestCase):

    def setUp(self):
        show = Show.objects.create(title='Community')
        season = Season.objects.create(show=show, num=1)
        episode = Episode.objects.create(season=season, num=4)
        self.torrent1 = Torrent.objects.create(
            episode=episode, name='torrent name', url='magnet:?blah'
        )
        self.torrent2 = Torrent.objects.create(
            episode=episode, name='another name', url='magnet:?blahblah'
        )

    def test_unique(self, utorrent):
        # Test good state
        download_1 = Download.objects.create(torrent=self.torrent1)
        download_2 = Download.objects.create(torrent=self.torrent2)
        download_1.full_clean()
        download_2.full_clean()

        # Test bad state
        with self.assertRaises(ValidationError):
            Download(torrent=self.torrent1).full_clean()

    def test_create(self, utorrent):
        # Creating a download should trigger a utorrent call
        download = Download.objects.create(torrent=self.torrent1)
        utorrent.download.assert_called_with(download)
        self.assertFalse(download.completed)

    def test_get_or_create(self, utorrent):
        # Getting or creating a new torrent should trigger utorrent
        download_1, created_1 = Download.objects.get_or_create(
            torrent=self.torrent1)
        self.assertTrue(created_1)
        utorrent.download.assert_called_with(download_1)

        download_2 = Download.objects.create(torrent=self.torrent2)

        # Getting an existing download should return same download
        utorrent.download.reset_mock()
        download_3, created_3 = Download.objects.get_or_create(
            torrent=self.torrent2)
        self.assertFalse(created_3)
        self.assertEqual(download_2, download_3)

        # It should also NOT trigger a utorrent call
        self.assertFalse(utorrent.download.called)
