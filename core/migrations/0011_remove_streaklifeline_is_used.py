# Generated by Django 5.0.2 on 2024-02-26 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_streaklifeline_is_on_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='streaklifeline',
            name='is_used',
        ),
    ]
