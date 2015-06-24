# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0009_remove_download_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='utorrent_hash',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
