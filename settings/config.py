import configparser
import appdirs
import os

DIR = appdirs.user_config_dir('rook')


def path():
    return os.path.join(DIR, 'config.ini')

config = configparser.ConfigParser()

defaults = {
    'general': {
        'videos': '~/Videos',
    },
    'utorrent': {
        'host': 'localhost:8080',
        'username': 'admin',
        'password': '',
    },
}


def read():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    config.read_dict(defaults)

    try:
        with open(path(), 'r+') as f:
            config.read_file(f)
    except FileNotFoundError:
        # create new config file with default settings
        write()


def write():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    with open(path(), 'w+') as f:
        config.write(f)
