# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventstatistics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventstatistic',
            name='timestamp',
            field=models.DateTimeField(null=True, verbose_name='Date and Time of Event'),
        ),
    ]