import threading
import shutil
import os
import logging

from torrents.models import Download
from settings import config

INTERVAL = 60.0

VIDEO_EXTS = ['.wmv', '.avi', '.flv', '.mov', '.mp4', '.mkv', '.mpg', '.m4v']

watch_started = False

timer = None

logger = logging.getLogger(__name__)


def start_watch():
    global watch_started

    if not watch_started:
        watch_started = True
        global timer
        timer = threading.Timer(INTERVAL, _repeat_watch)
        timer.daemon = True
        timer.start()


def _repeat_watch():
    global timer
    check_downloads()
    timer = threading.Timer(INTERVAL, _repeat_watch)
    timer.daemon = True
    timer.start()


def cancel_watch():
    global watch_started
    global timer
    if timer is not None:
        timer.cancel()
        timer = None
    watch_started = False


def check_downloads():
    # Copy across all completed downloads
    logger.debug('checking downloads')
    for download in Download.objects.all():
        if download.completed:
            logger.info('completed download found: {!r}'.format(download))
            # create a non-daemon thread so will not get terminated
            thread = threading.Thread(target=rename_download, args=(download,))
            thread.daemon = False
            thread.start()


def rename_download(download):
    logger.info('renaming download: {!r}'.format(download))
    episode = download.torrent.episode
    season = episode.season
    show = season.show
    name = '{} - S{:02d}E{:02d} - {}'.format(
        show.title, season.num, episode.num, episode.title)

    dest_folder = os.path.join(config.videos_path(), show.title)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for source in download.files:
        ext = os.path.splitext(source)[1]
        if ext in VIDEO_EXTS:
            dest = os.path.join(dest_folder, name) + ext
            logger.info('copying {} to {}'.format(source, dest))
            shutil.copyfile(source, dest)

    download.delete()
