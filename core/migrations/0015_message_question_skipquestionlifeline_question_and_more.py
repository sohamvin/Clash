# Generated by Django 5.0.3 on 2024-03-23 16:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_customuser_audience_poll'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.mcq'),
        ),
        migrations.AddField(
            model_name='skipquestionlifeline',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.mcq'),
        ),
        migrations.AddField(
            model_name='streaklifeline',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.mcq'),
        ),
        migrations.CreateModel(
            name='AudiancePoll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.mcq')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
