from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from unittest.mock import patch, MagicMock

from rook.test_runner import webdriver


class DownloadShowTest(StaticLiveServerTestCase):

    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def setUp(self):
        self.browser = webdriver()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def search_first_result(self, search_term):
        inputbox = self.browser.find_element_by_id('search')
        inputbox.send_keys(search_term)
        inputbox.send_keys(Keys.ENTER)

        results = self.browser.find_element_by_id('search_results')
        first_row = results.find_element_by_tag_name('tr')
        first_row.find_element_by_tag_name('a').click()

    def check_setting(self, setting, value):
        inputbox = self.browser.find_element_by_id(setting)
        self.assertEqual(inputbox.get_attribute('value'), value)

    def choose_setting(self, setting, label, default, value, password=False):
        label_elem = self.browser.find_element_by_id(
            '{}-label'.format(setting))
        self.assertEqual(label_elem.text, label)
        inputbox = self.browser.find_element_by_id(setting)
        self.assertEqual(inputbox.get_attribute('value'), default)
        inputbox.clear()
        inputbox.send_keys(value)

        if password:
            self.assertEquals(inputbox.get_attribute('type'), 'password')

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
        self.search_first_result('Game of Thrones')

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

    def test_episode_torrent_list(self):
        self.browser.get(self.live_server_url)

        # The user searches for a show they want to find torrents for
        self.search_first_result('community')

        # The user clicks the next episode they need
        episodes = self.browser.find_elements_by_class_name('episode')
        episode = next(e for e in episodes if e.text == '1 - Ladders')
        episode.find_element_by_tag_name('a').click()

        # The user sees a list of torrents for this episode (6x1)
        torrent_id = self.browser.find_element_by_id('torrents')
        torrents = torrent_id.find_elements_by_class_name('torrent')
        self.assertGreater(len(torrents), 0)
        for torrent in torrents:
            self.assertIn('Community', torrent.text)
            self.assertIn('6', torrent.text)
            self.assertIn('1', torrent.text)

        # The user sees that each torrent links to a torrent or magnet
        for torrent in torrents:
            torrent.find_element_by_tag_name('a')

    @patch('torrents.utorrent_ui.client.UTorrentClient')
    def test_utorrent_download(self, ut_client):
        self.browser.get(self.live_server_url)

        # The user starts their utorrent client
        ut_host = '192.168.0.105:9876'
        ut_user = 'the_user'
        ut_pass = 'changeme'
        ut_client.return_value = MagicMock()
        ut = ut_client.return_value

        # The user goes to settings to enter their utorrent settings
        settings = self.browser.find_element_by_id('settings')
        settings.click()
        self.choose_setting('utorrent-host', 'uTorrent host', 'localhost:8080',
                            ut_host)
        self.choose_setting('utorrent-username', 'uTorrent username', 'admin',
                            ut_user)
        self.choose_setting('utorrent-password', 'uTorrent password', '',
                            ut_pass, password=True)
        self.browser.find_element_by_id('apply').click()

        self.check_setting('utorrent-host', ut_host)
        self.check_setting('utorrent-username', ut_user)
        self.check_setting('utorrent-password', ut_pass)

        # The user wants to download an episode to their utorrent client
        self.search_first_result('the big bang theory')
        episode = self.browser.find_element_by_class_name('episode')
        episode.find_element_by_tag_name('a').click()

        # The user enthusiastically selects the first torrent they see
        torrent = self.browser.find_element_by_class_name('torrent')
        torrent.find_element_by_tag_name('a').click()

        # The user notices that uTorrent has added the torrent they selected
        ut_client.assert_called_with('http://{}/gui/'.format(ut_host),
                                     ut_user, ut_pass)
        self.assertTrue(ut.addurl.called)
