# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 21:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='uuid',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
