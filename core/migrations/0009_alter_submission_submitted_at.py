# Generated by Django 4.2.7 on 2024-02-07 08:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_current_score_submission_current_grading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='submitted_at',
            field=models.DateTimeField(verbose_name=datetime.datetime(2024, 2, 7, 14, 5, 58, 520089)),
        ),
    ]
