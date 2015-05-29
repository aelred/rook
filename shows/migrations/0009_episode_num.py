# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0008_episode_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
