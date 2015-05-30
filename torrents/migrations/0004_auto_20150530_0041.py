# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0003_torrent_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torrent',
            name='url',
            field=models.TextField(),
        ),
    ]
