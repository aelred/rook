# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0009_episode_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='title',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
