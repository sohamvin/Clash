# Generated by Django 4.2.10 on 2024-04-16 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_customuser_submitted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mcq',
            name='question_md',
            field=models.TextField(blank=True, default='Enter a Valid markdown'),
        ),
    ]
