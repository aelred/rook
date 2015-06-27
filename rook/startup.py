import urllib

import settings.config
import torrents.renamer
from shows.models import Show


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

    torrents.renamer.start_watch()
    Show.objects.start_update_thread()
