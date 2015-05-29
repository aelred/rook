from django.shortcuts import render

import tvdb_api
_t = tvdb_api.Tvdb()

from shows.models import Show


def home_page(request):
    return render(request, 'home.html')


def search(request):
    results = _t.search(request.GET['q'])
    shows = [Show.from_tvdb(result['id'], populate=False) for result in results]
    return render(request, 'search.html', {'results': shows})


def shows(request, id_):
    return render(request, 'shows.html', {'show': Show.from_tvdb(int(id_))})
