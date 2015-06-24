from utorrent import client


ut_client = None


def set_params(host, username, password):
    global ut_client
    ut_client = client.UTorrentClient('http://{}/gui/'.format(host),
                                      username, password, timeout=1)


def download(download_obj):
    ut_client.addurl(download_obj.torrent.url)
