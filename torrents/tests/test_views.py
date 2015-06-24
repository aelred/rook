from django.test import TestCase

from unittest.mock import patch

from shows.models import Show, Season, Episode
from torrents.models import Torrent, Download


class TorrentViewTest(TestCase):

    def setUp(self):
        show = Show.objects.create(title='Community')
        season = Season.objects.create(show=show, num=1)
        self.episode = Episode.objects.create(season=season, num=4)

    def test_torrent_results_appear(self):
        # look up the torrents for an episode
        response = self.client.get('/torrents/{}'.format(self.episode.id))
        self.assertTemplateUsed(response, 'torrents.html')

        torrents = response.context['torrents']
        self.assertGreater(len(torrents), 0)

        for torrent in torrents:
            self.assertContains(response, torrent.name)
            self.assertEquals(torrent.episode, self.episode)

    @patch('torrents.models.utorrent')
    def test_downloading_torrent(self, utorrent):
        # download a torrent
        torrent = Torrent.objects.create(
            episode=self.episode, name='a torrent',
            url='http://www.example.com/thing.torrent'
        )

        response = self.client.post('/downloads', data={'torrent': torrent.id})
        self.assertEqual(response.status_code, 201)

        # Make sure a download is created
        self.assertEqual(Download.objects.count(), 1)
        download = Download.objects.all()[0]
        self.assertEqual(download.torrent, torrent)

        # Make sure the torrent was added to utorrent
        utorrent.download.assert_called_with(torrent)
