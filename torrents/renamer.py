import threading

from torrents.models import Download

INTERVAL = 60.0


def start_watch():
    threading.Timer(INTERVAL, start_watch)
    check_downloads()


def check_downloads():
    # Delete all completed downloads - done individually because 'completed'
    # is a property, not a database field.
    for download in Download.objects.all():
        if download.completed:
            download.delete()
