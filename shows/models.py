from django.db import models
from django.core.urlresolvers import reverse

import tvdb_api
_t = tvdb_api.Tvdb()


class Show(models.Model):

    @classmethod
    def from_tvdb(cls, id_, populate=True):
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
        except cls.DoesNotExist:
            show = None

        tvdb_show = _t[id_]

        # fetch show if it isn't in database
        if show is None:
            tvdb_seasons = tvdb_show
            show = Show.objects.create(
                id=id_, title=tvdb_show['seriesname'], populated=populate
            )

        # populate show data if required
        if populate:
            for snum, tvdb_season in tvdb_show.items():
                season = Season.objects.create(show=show, num=snum)

                for enum, episode in tvdb_season.items():
                    Episode.objects.create(
                        season=season, num=enum, title=episode['episodename']
                    )

        return show

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
