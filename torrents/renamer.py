import threading

from torrents.models import Download

INTERVAL = 60.0

watch_started = False


def start_watch():
    global watch_started

    if not watch_started:
        watch_started = True
        threading.Timer(INTERVAL, _repeat_watch)
        check_downloads()


def _repeat_watch():
    threading.Timer(INTERVAL, _repeat_watch)
    check_downloads()


def check_downloads():
    # Delete all completed downloads - done individually because 'completed'
    # is a property, not a database field.
    for download in Download.objects.all():
        if download.completed:
            download.delete()
