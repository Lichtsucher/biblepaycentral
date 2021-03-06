# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-20 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Masternode',
            fields=[
                ('txid', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=64)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=30)),
                ('version', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MasternodeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('txid', models.CharField(max_length=64)),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=30)),
                ('version', models.IntegerField()),
            ],
        ),
    ]
