import urllib
import django

import settings.config
import torrents.renamer


def run():
    # load config settings on startup
    try:
        settings.config.read()
    except urllib.error.HTTPError:
        # Invalid uTorrent credentials
        pass
    except urllib.error.URLError:
        # Invalid uTorrent host
        pass

    django.setup()
    torrents.renamer.start_watch()
