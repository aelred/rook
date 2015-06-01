from lxml import html
import requests
import re
import cgi


_sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']


def to_bytes(size_str):
    num, suffix = size_str.split()
    mult = 1024 ** _sizes.index(suffix)
    return int(float(num) * mult)


class ThePirateBay:

    _search = '{url}/search/{query}/{page}/{sort}/{category}'
    _xpath = '//table[@id="searchResult"]//tr/td'
    _dat_re = re.compile(r'Uploaded\s+(?P<uploaded>.+)\s*,\s+'
                         'Size\s+(?P<size>.+)\s*,\s+ULed by')

    def __init__(self):
        self.url = 'https://thepiratebay.mn'
        self.sort = 99
        self.category = 205

    def search(self, term):
        page = 0
        term = cgi.escape(term)

        while True:
            response = requests.get(self._search.format(
                url=self.url, query=term, page=page, sort=self.sort,
                category=self.category
            ))
            tree = html.fromstring(response.text)

            names = tree.xpath(self._xpath + '/div[@class="detName"]/a/text()')
            seeders = tree.xpath(self._xpath + '[last()-1]/text()')
            leechers = tree.xpath(self._xpath + '[last()]/text()')
            magnets = tree.xpath(self._xpath +
                                 '/a/img[@alt="Magnet link"]/../@href')
            data = tree.xpath(self._xpath + '/font[@class="detDesc"]')

            # Check if no more results
            if len(names) == 0:
                return

            for name, seed, leech, magnet, dat in zip(names, seeders, leechers,
                                                      magnets, data):
                dtext = dat.text_content().replace('"', '').strip()
                re_match = self._dat_re.match(dtext).groupdict()

                yield {
                    'name': name, 'seeders': int(seed), 'leechers': int(leech),
                    'uploaded': re_match['uploaded'],
                    'size': to_bytes(re_match['size']), 'url': magnet
                }

            page += 1
