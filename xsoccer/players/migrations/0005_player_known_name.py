# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 06:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_auto_20170102_2138'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='known_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Known Name'),
        ),
    ]
