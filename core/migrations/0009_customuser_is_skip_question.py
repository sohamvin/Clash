# Generated by Django 5.0.2 on 2024-02-25 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_customuser_result_page_accessed'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_skip_question',
            field=models.BooleanField(default=True),
        ),
    ]
