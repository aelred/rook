from django.db import models

from torrents.thepiratebay import ThePirateBay
from shows.models import Episode

tpb = ThePirateBay()


class Torrent(models.Model):

    @classmethod
    def find_all(cls, episode):
        term = '{} S{:0>2}E{:0>2}'.format(episode.season.show.title,
                                          episode.season.num, episode.num)

        for result in tpb.search(term):
            yield Torrent.objects.create(episode=episode, name=result['name'],
                                         url=result['url'])

    episode = models.ForeignKey(Episode)
    name = models.TextField()
    url = models.TextField()  # this is not a URLField, to support magnet links
