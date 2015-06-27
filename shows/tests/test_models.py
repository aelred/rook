from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
import threading
import time

from shows.models import _active_sleep, Show, Season, Episode, _t

_house_tvdbid = 73255
_dexter_tvdbid = 79349


class ModelsTest(TestCase):

    def test_cache_off(self):
        # cache must be off so updating TV show data works correctly.
        # the rook database acts as a cache, so this doesn't cause too much
        # additional traffic
        self.assertFalse(_t.config['cache_enabled'])

    def test_active_sleep(self):
        start = time.time()
        _active_sleep(0.1)
        end = time.time()
        self.assertAlmostEqual(end-start, 0.1, delta=0.05)


class ShowModelTest(TestCase):

    def tearDown(self):
        Show.objects._update_thread_started = False

    def test_get_absolute_url(self):
        id_ = _house_tvdbid
        show = Show.objects.create(id=id_)
        self.assertEqual(show.get_absolute_url(), '/shows/{}'.format(id_))

    def test_from_tvdb(self):
        # Make sure model can load data on Dexter from thetvdb
        id_ = _dexter_tvdbid
        show = Show.objects.from_tvdb(id_)
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
        show = Show.objects.from_tvdb(id_, populate=False)
        self.assertEqual(show.title, 'House')

        # no seasons or episodes
        self.assertFalse(show.populated)
        self.assertEqual(Season.objects.count(), 0)
        self.assertEqual(Episode.objects.count(), 0)

    def test_from_tvdb_existing(self):
        # Make sure an existing show can be got from thetvdb
        id_ = _house_tvdbid
        show1 = Show.objects.from_tvdb(id_)
        show2 = Show.objects.from_tvdb(id_)

        # Make sure both shows are equal and valid in the database
        self.assertEquals(show1, show2)
        show1.full_clean()
        show2.full_clean()

    def test_from_tvdb_unpopulated(self):
        # Make sure accessing a previously unpopulated TVDB entry populates it
        id_ = _dexter_tvdbid
        show1 = Show.objects.from_tvdb(id_, populate=False)
        self.assertFalse(show1.populated)
        show2 = Show.objects.from_tvdb(id_)
        self.assertTrue(show2.populated)
        self.assertEquals(show1, show2)
        self.assertGreater(Season.objects.count(), 0)
        self.assertGreater(Episode.objects.count(), 0)

    def test_from_tvdb_unpopulated_twice(self):
        # Make sure show never populates even when an existing show is fetched
        id_ = _dexter_tvdbid
        Show.objects.from_tvdb(id_, populate=False)
        show = Show.objects.from_tvdb(id_, populate=False)
        self.assertFalse(show.populated)
        self.assertEqual(Season.objects.count(), 0)
        self.assertEqual(Episode.objects.count(), 0)

    @patch('shows.models.threading.Thread')
    def test_start_update_thread(self, thread):
        thread.return_value.daemon = False
        Show.objects.start_update_thread()
        thread.assert_called_with(target=Show.objects._update_thread)
        self.assertTrue(thread.return_value.daemon)
        thread.return_value.start.assert_called_with()

        # Make sure thread only starts once
        thread.reset_mock()
        Show.objects.start_update_thread()
        self.assertFalse(thread.called)

    @patch('shows.models._active_sleep')
    @patch('shows.models.Show.objects._update_shows')
    def test_update_thread(self, update_shows, active_sleep):
        # Create mock sleep event that wakes when we tell it to
        wake_event = threading.Event()

        def sleep_mock(interval):
            wake_event.wait()
            wake_event.clear()
        active_sleep.side_effect = sleep_mock

        Show.objects.start_update_thread()
        self.assertFalse(update_shows.called)
        active_sleep.assert_called_once_with(60 * 60 * 24)
        active_sleep.reset_mock()

        # wake up update thread
        wake_event.set()
        time.sleep(0.1)
        update_shows.assert_called_once_with()
        active_sleep.assert_called_once_with(60 * 60 * 24)
        active_sleep.reset_mock()

        # Make sure unsetting flag ends thread
        Show.objects._update_thread_started = False
        wake_event.set()
        time.sleep(0.1)
        self.assertFalse(active_sleep.called)

    @patch('shows.models._t')
    def test_update_shows(self, tvdb):
        id_ = -101
        t_show = tvdb.__getitem__.return_value
        t_show.__getitem__.return_value = 'My made-up show'
        season_1 = Mock()
        season_1.items.return_value = [
            (1, {'episodename': 'one'}), (2, {'episodename': 'two'})
        ]
        t_show.items.return_value = [(1, season_1)]

        # create show from data
        show = Show.objects.from_tvdb(id_)
        self.assertEqual(show.title, 'My made-up show')
        self.assertEqual(1, Season.objects.count())
        self.assertEqual(2, Episode.objects.count())

        # a new season is added to thetvdb and an episode changes title
        season_1.items.return_value[0][1]['episodename'] = 'One'
        season_2 = Mock()
        season_2.items.return_value = [(1, {'episodename': 'reboot'})]
        t_show.items.return_value.append((2, season_2))
        Show.objects._update_shows()
        self.assertEqual(2, Season.objects.count())
        self.assertEqual(3, Episode.objects.count())


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
