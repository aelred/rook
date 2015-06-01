# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0005_download'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='torrent',
            field=models.ForeignKey(default=None, to='torrents.Torrent'),
            preserve_default=False,
        ),
    ]
