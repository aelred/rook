import threading
import shutil
import os

from torrents.models import Download
from settings.config import config

INTERVAL = 60.0

watch_started = False

timer = None


def start_watch():
    global watch_started

    if not watch_started:
        watch_started = True
        global timer
        timer = threading.Timer(INTERVAL, _repeat_watch)
        timer.start()
        check_downloads()


def _repeat_watch():
    global timer
    timer = threading.Timer(INTERVAL, _repeat_watch)
    timer.start()
    check_downloads()


def cancel_watch():
    global watch_started
    global timer
    if timer is not None:
        timer.cancel()
        timer = None
    watch_started = False


def check_downloads():
    # Copy across all completed downloads
    for download in Download.objects.all():
        if download.completed:
            rename_download(download)
            download.delete()


def rename_download(download):
    episode = download.torrent.episode
    season = episode.season
    show = season.show
    videos = config['general']['videos']
    name = '{} - S{:02d}E{:02d} - {}'.format(
        show.title, season.num, episode.num, episode.title)

    for source in download.files:
        ext = os.path.splitext(source)[1]
        dest = os.path.join(videos, show.title, name) + ext
        shutil.copyfile(source, dest)

start_watch()
