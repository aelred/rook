from utorrent import client


ut_client = None


def set_params(host, username, password):
    global ut_client
    ut_client = client.UTorrentClient('http://{}/gui/'.format(host),
                                      username, password, timeout=1)


def download(download_obj):
    ut_client.addurl(download_obj.torrent.url)


def _get_data(download_obj):
    torrents = ut_client.list()[1]['torrents']
    data = next(t for t in torrents if t[0] == download_obj.utorrent_hash)
    return {
        'percent': data[4]
    }


def get_completed(download_obj):
    return _get_data(download_obj)['percent'] == 1000
