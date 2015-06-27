from selenium.webdriver.common.keys import Keys
from unittest.mock import patch, MagicMock
import os
import time

from .base import FunctionalTest


class DownloadShowTest(FunctionalTest):

    def search_first_result(self, search_term):
        inputbox = self.browser.find_element_by_id('search')
        inputbox.send_keys(search_term)
        inputbox.send_keys(Keys.ENTER)

        results = self.browser.find_element_by_id('search_results')
        first_row = results.find_element_by_tag_name('tr')
        first_row.find_element_by_tag_name('a').click()

    def test_lookup_show(self):
        # User opens the site and sees the title 'Rook'
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
        inputbox.send_keys('Doctor Who')
        inputbox.send_keys(Keys.ENTER)

        # The page now lists the show she was searching for and similar shows
        results = self.browser.find_element_by_id('search_results')
        rows = results.find_elements_by_tag_name('tr')
        self.assertIn('Doctor Who', [row.text for row in rows])
        self.assertIn('Doctor Who (2005)', [row.text for row in rows])

    def test_show_information(self):
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
        ut_host = '192.168.0.105:9876'
        ut_user = 'the_user'
        ut_pass = 'changeme'

        # The user starts their utorrent client
        ut_client.return_value = MagicMock()
        ut = ut_client.return_value
        fname = 'The Big Bang Theory S01E01.mkv'
        fpath = os.path.join(self.torrents_dir, fname)

        # The files in the torrent
        files = [(fname, '<VIDEO DATA HERE>'), ('info stuff.txt', 'hi')]

        def addurl(url):
            for name, data in files:
                path = os.path.join(self.torrents_dir, name)
                with open(path, 'a') as f:
                    f.write(data)
        ut.addurl.side_effect = addurl

        started_status = 201

        # The user goes to settings to enter their utorrent settings
        self.go_to_settings()
        self.choose_settings({
            'general-videos': self.videos_dir,
            'utorrent-host': ut_host,
            'utorrent-username': ut_user,
            'utorrent-password': ut_pass,
        })

        # The user wants to download an episode to their utorrent client
        self.search_first_result('the big bang theory')
        episodes = self.browser.find_elements_by_class_name('episode')
        episode = next(e for e in episodes if e.text == '1 - Pilot')
        episode.find_element_by_tag_name('a').click()

        # The user enthusiastically selects the first torrent they see
        torrent = self.browser.find_element_by_class_name('torrent')

        ut.list.return_value = (
            200,
            {
                'torrents': [[
                    'thehash', started_status, torrent.text, 100, 500, 50,
                    3171303424, 1000, 2000, 5, 0, 'BBT', 0, 0, 0, 0, 65536, -1,
                    0, '', '', 'Downloading 50.0 %', '18', 1426286134,
                    1426286134, '', self.torrents_dir, 0, 'HAHAHA'
                ]]
            }
        )

        ut.getfiles.return_value = (
            200,
            {
                'files': [
                    'something',
                    [
                        [
                            name, 100000000, 100000000, 2, 86, 96, False,
                            -1, -1, -1, -1, -1
                        ] for name, data in files
                    ]
                ],
                'build': 31466
            }
        )

        torrent.find_element_by_tag_name('a').click()

        # The user notices that uTorrent has added the torrent they selected
        ut_client.assert_called_with('http://{}/gui/'.format(ut_host),
                                     ut_user, ut_pass, timeout=1)
        self.assertTrue(ut.addurl.called)

        # The user sees that the torrent is downloading in the download folder
        self.assertIn(fname, os.listdir(self.torrents_dir))

        # The user looks in their videos directory and sees the download isn't
        # done yet...
        self.assertEquals(len(os.listdir(self.videos_dir)), 0)

        # The download completes
        ut.list.return_value[1]['torrents'][0][4] = 1000
        ut.list.return_value[1]['torrents'][0][5] = 100
        time.sleep(0.5)

        # The user looks at their videos directory again and sees a new folder!
        self.assertEquals(['The Big Bang Theory'], os.listdir(self.videos_dir))

        # Inside the folder is the downloaded video
        self.assertEquals(
            ['The Big Bang Theory - S01E01 - Pilot.mkv'],
            os.listdir(os.path.join(self.videos_dir, 'The Big Bang Theory')))

        # The user sees that the file is still in their torrents directory
        self.assertIn(fname, os.listdir(self.torrents_dir))

        # The user checks both files plays correctly (the contents is right)
        with open(os.path.join(self.videos_dir, 'The Big Bang Theory',
                               'The Big Bang Theory - S01E01 - Pilot.mkv'),
                  'r') as f:
            self.assertEquals(f.read(), '<VIDEO DATA HERE>')

        with open(fpath, 'r') as f:
            self.assertEquals(f.read(), '<VIDEO DATA HERE>')
