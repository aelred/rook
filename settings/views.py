from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse

import settings.config as config
from torrents import utorrent_ui


class Settings(View):

    def get(self, request):
        context = {
            '{}_{}'.format(section, key): value
            for section, values in config.config.items()
            for key, value in values.items()
        }
        return render(request, 'settings.html', context)

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
        utorrent_ui.set_params(**config.config['utorrent'])

        return redirect(reverse('settings'))
