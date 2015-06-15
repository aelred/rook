import threading

INTERVAL = 60.0


def start_watch():
    threading.Timer(INTERVAL, start_watch)
    check_downloads()


def check_downloads():
    pass
