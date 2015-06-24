from django.db import models

from torrents.thepiratebay import ThePirateBay
import torrents.utorrent_ui as utorrent
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

    # this is not a URLField, to support magnet links
    url = models.TextField(unique=True)


class DownloadManager(models.Manager):

    def get_or_create(self, *args, **kwargs):
        download, created = super().get_or_create(*args, **kwargs)
        if created:
            utorrent.download(download)
        return download, created

    def create(self, *args, **kwargs):
        download = Download(*args, **kwargs)
        download.utorrent_hash = utorrent.download(download)
        download.save(force_insert=True)
        return download


class Download(models.Model):

    objects = DownloadManager()

    torrent = models.OneToOneField(Torrent)
    utorrent_hash = models.CharField(max_length=40)

    @property
    def completed(self):
        return utorrent.get_completed(self)
