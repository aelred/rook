from django.conf.urls import patterns, include, url
from django.contrib import admin

from shows import views

urlpatterns = patterns(
    '',
    url(r'^$', views.home_page, name='home'),
    url(r'^search$', views.search, name='search'),
    url(r'^shows/(\d+)$', views.shows, name='shows'),
    url(r'^admin/', include(admin.site.urls)),
)
