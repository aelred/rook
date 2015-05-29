# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0007_episode'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='season',
            field=models.ForeignKey(to='shows.Season', default=0),
            preserve_default=False,
        ),
    ]
