from django.test import TestCase
from django.core.validators import URLValidator

import itertools

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
