# Generated by Django 5.0.3 on 2024-03-23 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_streaklifeline_conversion_streaklifeline_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='teammate_one',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]
