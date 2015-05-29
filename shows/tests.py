from django.test import TestCase
from django.core.exceptions import ValidationError

from shows.models import Show, Season, Episode

_house_tvdbid = 73255
_dexter_tvdbid = 79349


class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ShowSearchTest(TestCase):

    def test_search_results_page_shows_results(self):
        response = self.client.get('/search?q=fullmetal')
        self.assertTemplateUsed(response, 'search.html')

        results = response.context['results']
        titles = [result.title for result in results]
        self.assertIn('Fullmetal Alchemist', titles)
        self.assertIn('Fullmetal Alchemist: Brotherhood', titles)

        self.assertContains(response, 'Fullmetal Alchemist')
        self.assertContains(response, 'Fullmetal Alchemist: Brotherhood')

    def test_searching_doesnt_fetch_all_data(self):
        response = self.client.get('/search?q=house')
        results = response.context['results']

        # check there are results
        self.assertGreater(len(results), 0)
        self.assertGreater(Show.objects.count(), 0)
        # but make sure NO season or episode data has downloaded
        self.assertEquals(Season.objects.count(), 0)
        self.assertEquals(Episode.objects.count(), 0)


class ShowPageTest(TestCase):

    def test_show_page_has_show_info(self):
        response = self.client.get('/shows/{}'.format(_house_tvdbid))
        self.assertTemplateUsed(response, 'shows.html')

        show = response.context['show']
        self.assertEquals(show.title, 'House')

        self.assertContains(response, 'House')
        self.assertContains(response, 'Season 1')
        self.assertContains(response, '24')
        self.assertContains(response, 'Failure to Communicate')
        self.assertContains(response, 'Season 8')


class ShowModelTest(TestCase):

    def test_get_absolute_url(self):
        id_ = _house_tvdbid
        show = Show.objects.create(id=id_)
        self.assertEqual(show.get_absolute_url(), '/shows/{}'.format(id_))

    def test_from_tvdb(self):
        # Make sure model can load data on Dexter from thetvdb
        id_ = _dexter_tvdbid
        show = Show.from_tvdb(id_)
        self.assertEqual(show.id, id_)
        self.assertEqual(show.title, 'Dexter')
        self.assertTrue(show.populated)
        seasons = show.season_set.all()
        self.assertEquals(list(range(8)), [s.num for s in seasons][:8])

        season2 = show.season_set.get(num=2)
        episodes = season2.episode_set.all()
        self.assertEquals(list(range(1, 13)), [e.num for e in episodes])

        ep2x3 = season2.episode_set.get(num=3)
        self.assertEquals('An Inconvenient Lie', ep2x3.title)

    def test_from_tvdb_without_populating(self):
        # test we can get show data without season or episode data
        id_ = _house_tvdbid
        show = Show.from_tvdb(id_, populate=False)
        self.assertEqual(show.title, 'House')

        # no seasons or episodes
        self.assertFalse(show.populated)
        self.assertEqual(Season.objects.count(), 0)
        self.assertEqual(Episode.objects.count(), 0)

    def test_from_tvdb_existing(self):
        # Make sure an existing show can be got from thetvdb
        id_ = _house_tvdbid
        show1 = Show.from_tvdb(id_)
        show2 = Show.from_tvdb(id_)

        # Make sure both shows are equal and valid in the database
        self.assertEquals(show1, show2)
        show1.full_clean()
        show2.full_clean()

    def test_from_tvdb_unpopulated(self):
        # Make sure accessing a previously unpopulated TVDB entry populates it
        id_ = _dexter_tvdbid
        show1 = Show.from_tvdb(id_, populate=False)
        self.assertFalse(show1.populated)
        show2 = Show.from_tvdb(id_)
        self.assertTrue(show2.populated)
        self.assertEquals(show1, show2)
        self.assertGreater(Season.objects.count(), 0)
        self.assertGreater(Episode.objects.count(), 0)

    def test_from_tvdb_unpopulated_twice(self):
        # Make sure show never populates even when an existing show is fetched
        id_ = _dexter_tvdbid
        Show.from_tvdb(id_, populate=False)
        show = Show.from_tvdb(id_, populate=False)
        self.assertFalse(show.populated)
        self.assertEqual(Season.objects.count(), 0)
        self.assertEqual(Episode.objects.count(), 0)


class SeasonModelTest(TestCase):

    def test_same_show_or_num(self):
        # can create seasons for the same show, or with the same number
        # without raising an exception.
        dexter = Show.objects.create(title='Dexter')
        scrubs = Show.objects.create(title='Scrubs')
        Season.objects.create(show=dexter, num=1)
        Season.objects.create(show=dexter, num=2)
        Season.objects.create(show=scrubs, num=2)

    def test_uniqueness_constraint(self):
        # cannot create a season with the same show AND number
        dexter = Show.objects.create(title='Dexter')
        Season.objects.create(show=dexter, num=1)

        season = Season(show=dexter, num=1)
        with self.assertRaises(ValidationError):
            season.full_clean()


class EpisodeModelTest(TestCase):

    def setUp(self):
        show = Show.objects.create(title='Dexter')
        self.season_2 = Season.objects.create(show=show, num=2)
        self.season_3 = Season.objects.create(show=show, num=3)

    def test_optional_title(self):
        # shouldn't raise any exceptions
        Episode.objects.create(season=self.season_2, num=8).full_clean()
        Episode.objects.create(
            season=self.season_3, num=2, title=None
        ).full_clean()

    def test_same_season_or_num(self):
        # can create episodes for the same season, or with the same number
        # without raising an exception.
        Episode.objects.create(season=self.season_2, num=10)
        Episode.objects.create(season=self.season_2, num=20)
        Episode.objects.create(season=self.season_3, num=20)

    def test_uniqueness_constraint(self):
        # cannot create an episode with the same season AND number
        Episode.objects.create(season=self.season_2, num=5, title='distinct')

        episode = Episode(season=self.season_2, num=5, title='different')
        with self.assertRaises(ValidationError):
            episode.full_clean()
