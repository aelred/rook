from django.shortcuts import render

import itertools

from shows.models import Episode
from torrents.models import Torrent


def torrents(request, episode_id):
    episode = Episode.objects.get(pk=int(episode_id))
    torrents = list(itertools.islice(Torrent.find_all(episode), 10))
    return render(request, 'torrents.html', {'torrents': torrents})
