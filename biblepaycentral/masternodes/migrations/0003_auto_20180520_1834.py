# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-20 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masternodes', '0002_auto_20180520_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masternodehistory',
            name='txid',
            field=models.CharField(max_length=100),
        ),
    ]
