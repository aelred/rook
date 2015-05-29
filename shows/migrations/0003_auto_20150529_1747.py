# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0002_show_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='title',
            field=models.TextField(),
        ),
    ]
