# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-07-18 12:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_auto_20160709_1316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coins',
            old_name='coin_code',
            new_name='serialised_code_rnd_tau_gam',
        ),
    ]