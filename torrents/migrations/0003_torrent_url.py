# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0002_torrent_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='torrent',
            name='url',
            field=models.URLField(default=None),
            preserve_default=False,
        ),
    ]
