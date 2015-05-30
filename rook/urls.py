from django.conf.urls import patterns, include, url
from django.contrib import admin

import shows.views as show_views
import torrents.views as torrent_views

urlpatterns = patterns(
    '',
    url(r'^$', show_views.home_page, name='home'),
    url(r'^search$', show_views.search, name='search'),
    url(r'^shows/(\d+)$', show_views.shows, name='shows'),
    url(r'^torrents/(\d+)$', torrent_views.torrents, name='torrents'),
    url(r'^admin/', include(admin.site.urls)),
)
