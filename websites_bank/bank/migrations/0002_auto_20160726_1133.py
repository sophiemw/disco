# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-07-26 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userswhohavedoublespent',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]