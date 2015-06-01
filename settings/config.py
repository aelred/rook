import configparser
import appdirs
import os

dir_ = appdirs.user_config_dir('rook')
path = os.path.join(dir_, 'config.ini')

if not os.path.exists(dir_):
    os.makedirs(dir_)

config = configparser.ConfigParser()

defaults = {
    'utorrent': {
        'host': 'localhost:8080',
        'username': 'admin',
        'password': ''
    }
}


def read():
    config.read_dict(defaults)
    with open(path, 'r+') as f:
        config.read(f)


def write():
    with open(path, 'w+') as f:
        config.write(f)
