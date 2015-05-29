from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class DownloadShowTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_lookup_show(self):
        # User opens the site and sees the title 'Rook'
        self.browser.get(self.live_server_url)
        self.assertIn('Rook', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Rook', header_text)

        # User sees a text box suggesting she searches for a TV show
        inputbox = self.browser.find_element_by_id('search')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Search for a TV show'
        )

        # The user inputs her favourite show in the box and hits enter
        inputbox.send_keys('House')
        inputbox.send_keys(Keys.ENTER)

        # The page now lists the show she was searching for and similar shows
        results = self.browser.find_element_by_id('search_results')
        rows = results.find_elements_by_tag_name('tr')
        self.assertIn('House', [row.text for row in rows])
        self.assertIn('House of Cards (US)', [row.text for row in rows])

    def test_show_information(self):
        self.browser.get(self.live_server_url)

        # The user searches for a new show she's heard of
        inputbox = self.browser.find_element_by_id('search')
        inputbox.send_keys('Game of Thrones')
        inputbox.send_keys(Keys.ENTER)

        # The user selects the show they want
        results = self.browser.find_element_by_id('search_results')
        rows = results.find_elements_by_tag_name('tr')
        show_link = next(row for row in rows if row.text == 'Game of Thrones')
        show_link.find_element_by_tag_name('a').click()

        # The user sees some information about the show's seasons...
        season_list = self.browser.find_element_by_id('seasons')
        seasons = season_list.find_elements_by_class_name('season')
        season_titles = [
            s.find_element_by_class_name('season-title').text for s in seasons
        ]
        self.assertEquals(
            ['Specials', 'Season 1', 'Season 2', 'Season 3', 'Season 4'],
            season_titles[:5]
        )

        # ...and accidentally reads a spoiler
        season_3 = next(
            s for s in seasons
            if s.find_element_by_class_name('season-title').text == 'Season 3'
        )
        episodes = season_3.find_elements_by_class_name('episode')
        episode_titles = [e.text for e in episodes]
        self.assertIn('9 - The Rains of Castamere', episode_titles)
