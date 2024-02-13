# Generated by Django 5.0.1 on 2024-02-09 11:53

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mcq',
            fields=[
                ('question_id', models.IntegerField(primary_key=True, serialize=False)),
                ('question_md', models.CharField(default='Enter a Valid markdown', max_length=255)),
                ('a', models.CharField(max_length=255)),
                ('b', models.CharField(max_length=255)),
                ('c', models.CharField(max_length=255)),
                ('d', models.CharField(max_length=255)),
                ('correct', models.CharField(choices=[('a', models.CharField(max_length=255)), ('b', models.CharField(max_length=255)), ('c', models.CharField(max_length=255)), ('d', models.CharField(max_length=255))], max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('authors_note', models.CharField(blank=True, max_length=255)),
                ('senior', models.BooleanField(default=False)),
                ('correct_responses', models.IntegerField(default=0)),
                ('total_responses', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('team_id', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=256, unique=True)),
                ('teammate_one', models.CharField(max_length=300)),
                ('teammate_two', models.CharField(blank=True, max_length=300)),
                ('team_score', models.IntegerField(default=0)),
                ('current_question', models.IntegerField(default=1)),
                ('previous_question', models.BooleanField(default=False)),
                ('question_streak', models.IntegerField(default=0)),
                ('senior_team', models.BooleanField(default=False)),
                ('Questions_to_list', models.TextField(default='NOTHING')),
                ('total_questions', models.IntegerField(default=0)),
                ('correct_questions', models.IntegerField(default=0)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StreakLifeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('questions', models.TextField(default='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('submission_id', models.AutoField(primary_key=True, serialize=False)),
                ('selected_option', models.CharField(choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')], max_length=1)),
                ('status', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('current_grading', models.IntegerField(default=0)),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mcq')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
