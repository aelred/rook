from django.test import TestCase
from django.core.validators import URLValidator

import itertools
from unittest.mock import patch

from torrents.thepiratebay import to_bytes, ThePirateBay

validate = URLValidator()


class ToBytesTest(TestCase):

    def test_to_bytes(self):
        self.assertEquals(to_bytes('5 B'), 5)
        self.assertEquals(to_bytes('1 KiB'), 1024)
        self.assertEquals(to_bytes('3.5 MiB'), 3670016)
        self.assertEquals(to_bytes('45.2\xa0GiB'), 48533130444)


class ThePirateBayTest(TestCase):

    def test_search(self):
        tpb = ThePirateBay()
        torrents = tpb.search('game of thrones S05E03')

        # make sure first 10 torrents have expected information
        has_torrents = False
        for torrent in itertools.islice(torrents, 10):
            has_torrents = True
            self.assertIsInstance(torrent['name'], str)
            self.assertIsInstance(torrent['seeders'], int)
            self.assertIsInstance(torrent['leechers'], int)
            self.assertIsInstance(torrent['uploaded'], str)
            self.assertIsInstance(torrent['size'], int)
            self.assertIsInstance(torrent['url'], str)

        self.assertTrue(has_torrents)

    @patch('torrents.thepiratebay.requests.get')
    def test_search_mocked_page(self, rget):
        rget.return_value.text = """
        <html>
            <table id="searchResult">
                <tbody>
                    <tr>
                        <td>
                            <div class="detName">
                                <a>A name</a>
                            </div>
                            <a href="a magnet link">
                                <img alt="Magnet link"></img>
                            </a>
                            <font class="detDesc">
                                "Uploaded "
                                <b>Really recently</b>
                                ", Size 300 B, ULed by "
                                <a class="detDesc" href="some guy">some guy</a>
                            </font>
                        </td>
                        <td>80085</td>
                        <td>1337</td>
                    </tr>
                </tbody>
            </table>
        </html>
        """
        tpb = ThePirateBay()
        torrents = tpb.search('whatever')

        # make sure search finds the one torrent
        torrent = next(torrents)
        self.assertEqual(
            torrent,
            {
                'name': 'A name',
                'seeders': 80085,
                'leechers': 1337,
                'uploaded': 'Really recently',
                'size': 300,
                'url': 'a magnet link'
            }
        )

        # make sure the next torrent is the same result
        # (this is because every page is the same due to the mocking)
        self.assertEqual(torrent, next(torrents))
