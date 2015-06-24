from utorrent import client

import time


ut_client = None


def set_params(host, username, password):
    global ut_client
    ut_client = client.UTorrentClient('http://{}/gui/'.format(host),
                                      username, password, timeout=1)


def download(torrent):
    ut_client.addurl(torrent.url)

    # get hash of added torrent
    torrents = ut_client.list()[1]['torrents']

    while True:
        try:
            data = next(t for t in torrents if t[2] == torrent.name)
        except StopIteration:
            time.sleep(0.1)
        else:
            break
    return data[0]


def _get_data(download):
    torrents = ut_client.list()[1]['torrents']
    data = next(t for t in torrents if t[0] == download.utorrent_hash)
    return {
        'percent': data[4]
    }


def get_completed(download):
    return _get_data(download)['percent'] == 1000
