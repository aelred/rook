from django.test import TestCase

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
