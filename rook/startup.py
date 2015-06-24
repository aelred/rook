import urllib

import settings.config


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
