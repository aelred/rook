import threading

from torrents.models import Download

INTERVAL = 60.0


def start_watch():
    threading.Timer(INTERVAL, start_watch)
    check_downloads()


def check_downloads():
    # Delete all completed downloads
    Download.objects.filter(completed=True).delete()
