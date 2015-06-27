from django.db import models
from django.core.urlresolvers import reverse
import threading
import time

import tvdb_api
_t = tvdb_api.Tvdb(cache=False)


def _active_sleep(interval):
    # Sleep, but occasionally wake to check the system time.
    # Takes into account time when the system is off.
    sleep_time = min(60, interval / 10)
    start = time.time()
    while time.time() - start < interval:
        time.sleep(sleep_time)


class ShowManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_thread_started = False

    def from_tvdb(self, id_, populate=True):
        # Load a show from the tvdb using a TVDB id.
        try:
            # get show if it already exists
            show = Show.objects.get(pk=id_)

            # populate show if necessary
            if show.populated or not populate:
                return show
            else:
                show.populated = True
                show.save()
        except Show.DoesNotExist:
            show = None

        tvdb_show = _t[id_]

        # fetch show if it isn't in database
        if show is None:
            show = Show.objects.create(
                id=id_, title=tvdb_show['seriesname'], populated=populate
            )

        # populate show data if required
        if populate:
            self._populate_show(show, tvdb_show)

        return show

    def start_update_thread(self):
        if not self._update_thread_started:
            thread = threading.Thread(target=self._update_thread)
            thread.daemon = True
            self._update_thread_started = True
            thread.start()

    def _update_thread(self):
        while self._update_thread_started:
            _active_sleep(60 * 60 * 24)
            self._update_shows()

    def _update_shows(self):
        for show in Show.objects.all():
            self._populate_show(show, _t[show.id])

    def _populate_show(self, show, tvdb_show):
        for snum, tvdb_season in tvdb_show.items():
            season = Season.objects.update_or_create(show=show, num=snum)[0]

            for enum, episode in tvdb_season.items():
                Episode.objects.update_or_create(
                    season=season, num=enum,
                    defaults={'title': episode['episodename']}
                )


class Show(models.Model):

    objects = ShowManager()

    title = models.TextField()
    populated = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('shows', args=[self.id])


class Season(models.Model):
    show = models.ForeignKey(Show)
    num = models.IntegerField()

    class Meta:
        unique_together = ('show', 'num')


class Episode(models.Model):
    season = models.ForeignKey(Season)
    num = models.IntegerField()
    title = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('season', 'num')
