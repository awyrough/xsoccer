# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-09 04:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0003_auto_20170105_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='surface',
            field=models.CharField(default='Unknown', max_length=100, null=True),
        ),
    ]