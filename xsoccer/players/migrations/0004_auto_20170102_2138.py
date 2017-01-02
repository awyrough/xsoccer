# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 21:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_auto_20170102_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='birth_date',
            field=models.DateField(null=True, verbose_name='Birth Date'),
        ),
        migrations.AlterField(
            model_name='player',
            name='birth_place',
            field=models.CharField(max_length=255, null=True, verbose_name='Birth Place'),
        ),
        migrations.AlterField(
            model_name='player',
            name='country',
            field=models.CharField(max_length=255, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='player',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='player',
            name='height',
            field=models.FloatField(default=0.0, null=True, verbose_name='Height (cm)'),
        ),
        migrations.AlterField(
            model_name='player',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='player',
            name='nationality',
            field=models.CharField(max_length=255, null=True, verbose_name='Nationality'),
        ),
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.CharField(choices=[('Goalkeeper', 'Goalkeeper'), ('Wing Back', 'Wing Back'), ('Full Back', 'Full Back'), ('Central Defender', 'Central Defender'), ('Defensive Midfielder', 'Defensive Midfielder'), ('Attacking Midfielder', 'Attacking Midfielder'), ('Central Midfielder', 'Central Midfielder'), ('Winger', 'Winger'), ('Striker', 'Striker'), ('Second Striker', 'Second Striker')], max_length=255, null=True, verbose_name='Real Position'),
        ),
        migrations.AlterField(
            model_name='player',
            name='position_side',
            field=models.CharField(choices=[('Left', 'Left'), ('Right', 'Right'), ('Centre', 'Centre'), ('Left/Centre', 'Left/Centre'), ('Centre/Right', 'Centre/Right'), ('Left/Centre/Right', 'Left/Centre/Right'), ('Left/Right', 'Left/Right')], max_length=255, null=True, verbose_name='Position Side of Choice'),
        ),
        migrations.AlterField(
            model_name='player',
            name='uuid',
            field=models.CharField(max_length=255, unique=True, verbose_name='Opta uID'),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight',
            field=models.FloatField(default=0.0, null=True, verbose_name='Weight (kg)'),
        ),
    ]
