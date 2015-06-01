import settings.config


def run():
    # load config settings on startup
    settings.config.read()
