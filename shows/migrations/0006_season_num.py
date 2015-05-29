# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0005_season_show'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
