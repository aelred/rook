from django.shortcuts import render
from django.http import HttpResponse

import itertools

from shows.models import Episode
from torrents.models import Torrent, Download


def torrents(request, episode_id):
    episode = Episode.objects.get(pk=int(episode_id))
    torrents = list(itertools.islice(Torrent.find_all(episode), 10))
    return render(request, 'torrents.html', {'torrents': torrents})


def downloads(request):
    torrent = Torrent.objects.get(pk=int(request.POST['torrent']))
    Download.objects.create(torrent=torrent)
    return HttpResponse('', status=201)
