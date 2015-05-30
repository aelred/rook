# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='torrent',
            name='name',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
