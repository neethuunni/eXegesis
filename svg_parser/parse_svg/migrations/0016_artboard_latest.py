# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-07 09:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parse_svg', '0015_revision'),
    ]

    operations = [
        migrations.AddField(
            model_name='artboard',
            name='latest',
            field=models.BooleanField(default=True),
        ),
    ]
