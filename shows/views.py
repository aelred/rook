from django.shortcuts import render

import tvdb_api
_t = tvdb_api.Tvdb()


def home_page(request):
    return render(request, 'home.html')


def search(request):
    results = _t.search(request.GET['q'])
    titles = [show['seriesname'] for show in results]
    return render(request, 'search.html', {'results': titles})
