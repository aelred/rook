# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0011_auto_20150529_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='populated',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
