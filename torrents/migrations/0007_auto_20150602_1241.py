# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0006_download_torrent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='torrent',
            field=models.OneToOneField(to='torrents.Torrent'),
        ),
        migrations.AlterField(
            model_name='torrent',
            name='url',
            field=models.TextField(unique=True),
        ),
    ]
