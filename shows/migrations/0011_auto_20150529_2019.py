# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0010_episode_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('season', 'num')]),
        ),
        migrations.AlterUniqueTogether(
            name='season',
            unique_together=set([('show', 'num')]),
        ),
    ]
