from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse

import settings.config as config
from torrents import utorrent_ui

import urllib.error

UTORRENT_CONNECTION_ERROR = (
    'uTorrent connection failed. Please check the uTorrent host is correct.'
)

UTORRENT_AUTHORIZATION_ERROR = (
    'uTorrent authorization failed. Please check the uTorrent username and '
    'password is correct.'
)


class Settings(View):

    def context(self):
        return {
            '{}_{}'.format(section, key): value
            for section, values in config.config.items()
            for key, value in values.items()
        }

    def get(self, request):
        return render(request, 'settings.html', self.context())

    def post(self, request):
        # change setings in config
        for setting, value in request.POST.items():
            # get settings from POST data
            try:
                section, key = setting.split('-')
            except ValueError:
                continue
            if section in config.defaults and key in config.defaults[section]:
                config.config[section][key] = value

        # write config to file
        config.write()

        # update uTorrent parameters
        try:
            utorrent_ui.set_params(**config.config['utorrent'])
        except urllib.error.HTTPError:
            # Invalid uTorrent credentials
            context = self.context()
            context['error'] = UTORRENT_AUTHORIZATION_ERROR
            return render(request, 'settings.html', context)
        except urllib.error.URLError:
            # Invalid uTorrent host
            context = self.context()
            context['error'] = UTORRENT_CONNECTION_ERROR
            return render(request, 'settings.html', context)

        return redirect(reverse('settings'))
