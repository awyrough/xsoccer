# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 20:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventstatistics', '0004_auto_20170112_2007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventstatistic',
            old_name='relative_time',
            new_name='relative_seconds',
        ),
    ]