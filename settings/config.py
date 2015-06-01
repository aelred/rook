import configparser
import appdirs
import os

dir_ = appdirs.user_config_dir('rook')


def path():
    return os.path.join(dir_, 'config.ini')

config = configparser.ConfigParser()

defaults = {
    'utorrent': {
        'host': 'localhost:8080',
        'username': 'admin',
        'password': ''
    }
}


def read():
    if not os.path.exists(dir_):
        os.makedirs(dir_)

    config.read_dict(defaults)

    try:
        with open(path(), 'r+') as f:
            config.read(f)
    except FileNotFoundError:
        # create new config file with default settings
        write()


def write():
    if not os.path.exists(dir_):
        os.makedirs(dir_)

    with open(path(), 'w+') as f:
        config.write(f)
