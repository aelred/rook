from django.test import TestCase

from shows.models import Show, Season, Episode


class TorrentViewTest(TestCase):

    def test_torrent_results_appear(self):
        # look up the torrents for an episode
        show = Show.objects.create(title='Community')
        season = Season.objects.create(show=show, num=1)
        episode = Episode.objects.create(season=season, num=4)
        response = self.client.get('/torrents/{}'.format(episode.id))
        self.assertTemplateUsed(response, 'torrents.html')

        torrents = response.context['torrents']
        self.assertGreater(len(torrents), 0)

        for torrent in torrents:
            self.assertContains(response, torrent.name)
            self.assertEquals(torrent.episode, episode)
