from django.test import TestCase

from unittest.mock import patch, Mock

import torrents.utorrent_ui


class TestUTorrent(TestCase):

    @patch('torrents.utorrent_ui.ut_client')
    def test_download(self, ut_client):
        download = Mock()
        download.torrent.url = 'a url'
        torrents.utorrent_ui.download(download)
        ut_client.addurl.assert_called_with('a url')

    @patch('torrents.utorrent_ui.client.UTorrentClient')
    def test_set_params(self, client):
        old_client = torrents.utorrent_ui.ut_client
        torrents.utorrent_ui.set_params('1.2.3.4:8', 'me', 'not telling')
        client.assert_called_with('http://1.2.3.4:8/gui/', 'me', 'not telling')
        self.assertNotEqual(old_client, torrents.utorrent_ui.ut_client)
