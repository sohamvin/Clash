# Generated by Django 5.0.2 on 2024-02-25 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_customuser_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
