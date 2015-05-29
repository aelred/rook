from django.test import TestCase


class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ShowSearchTest(TestCase):

    def test_search_results_page_shows_results(self):
        response = self.client.get('/search?q=fullmetal')
        self.assertTemplateUsed(response, 'search.html')

        results = response.context['results']
        self.assertIn('Fullmetal Alchemist', results)
        self.assertIn('Fullmetal Alchemist: Brotherhood', results)

        self.assertContains(response, 'Fullmetal Alchemist')
        self.assertContains(response, 'Fullmetal Alchemist: Brotherhood')
