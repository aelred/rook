from django.test import TestCase

from unittest.mock import patch, Mock

import torrents.utorrent_ui


UT_LIST = (
    200,
    {
        'label': [['tv', 1]],
        'torrentc': '739195965',
        'torrents': [
            [
                '028ADCDD7A96F7F151BC0FB618E0777E2B2F69F9', 201,
                'Firefly.2002.01x03.x264-BLOW', 5972552749, 1000,
                5972552749, 3351314432, 561, 45974, 53, 210596, 'tv', 1, 3, 0,
                0, 82552, -1, 0, '', '', 'Seeding 100.0 %', '1db11b69',
                1426286134, 1426289247, '',
                'C:\\downloads\\Firefly.2002.01x03.x264-BLOW', 0, 'C53FC3CE'
            ],
            [
                'BA9FFD0202F6A101376D9163CA7FB9D474DEA8AC', 201,
                '[ChoeyXD] One Piece 355 (Dual Audio) [278F9B0B].mkv',
                430939486, 9, 3997696, 0, 0, 819, 481801, 23941076, 'video',
                0, 2, 3, 3, 196608, 1, 426941790, '', '', 'Downloading 0.9 %',
                'f', 1435173243, 0, '', 'D:\\Torrents', 0, '1E9F6125'
            ]
        ],
        'rssfeeds': [],
        'build': 31466,
        'rssfilters': []
    }
)


class TestUTorrent(TestCase):

    def setUp(self):
        self.down_1 = Mock()
        self.down_1.utorrent_hash = '028ADCDD7A96F7F151BC0FB618E0777E2B2F69F9'
        self.down_2 = Mock()
        self.down_2.utorrent_hash = 'BA9FFD0202F6A101376D9163CA7FB9D474DEA8AC'

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
        client.assert_called_with('http://1.2.3.4:8/gui/', 'me', 'not telling',
                                  timeout=1)
        self.assertNotEqual(old_client, torrents.utorrent_ui.ut_client)

    @patch('torrents.utorrent_ui.ut_client')
    def test_get_completed(self, ut_client):
        ut_client.list.return_value = UT_LIST

        self.assertTrue(torrents.utorrent_ui.get_completed(self.down_1))
        self.assertFalse(torrents.utorrent_ui.get_completed(self.down_2))
