# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0012_show_populated'),
    ]

    operations = [
        migrations.CreateModel(
            name='Torrent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('episode', models.ForeignKey(to='shows.Episode')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
