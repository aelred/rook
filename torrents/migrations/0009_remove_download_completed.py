# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0008_download_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='download',
            name='completed',
        ),
    ]
