# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-13 08:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=50)),
                ('image', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=100)),
            ],
        ),
    ]