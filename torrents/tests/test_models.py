from django.test import TestCase

import itertools

from shows.models import Show, Season, Episode
from torrents.models import Torrent


class TorrentModelTest(TestCase):

    def test_find_all(self):
        # test searching for torrents
        show = Show.objects.create(title='Breaking Bad')
        season = Season.objects.create(show=show, num=3)
        episode = Episode.objects.create(season=season, num=2)

        torrents = Torrent.find_all(episode)

        has_torrents = False
        for torrent in itertools.islice(torrents, 10):
            has_torrents = True
            torrent.clean()
            self.assertEquals(torrent.episode, episode)
            self.assertIn('breaking bad',
                          torrent.name.lower().replace('.', ' '))
            self.assertIn('3', torrent.name)
            self.assertIn('2', torrent.name)

        self.assertTrue(has_torrents)
