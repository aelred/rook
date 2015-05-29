# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0004_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='show',
            field=models.ForeignKey(to='shows.Show', default=None),
            preserve_default=False,
        ),
    ]
