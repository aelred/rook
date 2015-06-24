# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0007_auto_20150602_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
