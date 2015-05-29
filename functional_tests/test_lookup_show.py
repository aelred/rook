from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class LookupShowTest(StaticLiveServerTestCase):

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
