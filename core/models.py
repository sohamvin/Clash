from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils import timezone
import uuid
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
import random

from django.contrib.auth import get_user_model

class Mcq(models.Model):
    question_id = models.IntegerField(primary_key = True)
    question_md = models.CharField(max_length=255, blank=False, default="Enter a Valid markdown")
    a = models.CharField(max_length=255, blank=False)
    b = models.CharField(max_length=255, blank=False)
    c = models.CharField(max_length=255, blank=False)
    d = models.CharField(max_length=255, blank=False)
    correct = models.CharField(max_length=255, blank=False, choices=(("a", a), ("b", b), ("c", c), ("d", d) ))
    author = models.CharField(max_length=255, blank=False)
    authors_note = models.CharField(max_length=255, blank=True)
    senior = models.BooleanField(default=False)
    correct_responses = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)

    def __str__(self):
        return str(self.question_id)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    team_id = models.CharField(max_length=256, primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=256, unique=True) # overrided , but must be team name , not username of user
    teammate_one = models.CharField(max_length=300, unique = True)
    teammate_two = models.CharField(max_length=300, blank=True)
    team_score = models.IntegerField(default=0)
    current_question = models.IntegerField(default=1, blank=False)
    previous_question = models.BooleanField(default=False, blank=False)
    question_streak = models.IntegerField(default=0)
    senior_team = models.BooleanField(default=False)
    Questions_to_list = models.TextField(default="NOTHING")
    total_questions = models.IntegerField(default=0, blank=False)
    correct_questions = models.IntegerField(default=0, blank=False)
    is_first_visit = models.BooleanField(default=True, blank=False) # to set the end_time at first visit
    end_time = models.DateTimeField(null=True, blank=True, default=timezone.now)
    is_skip_question = models.BooleanField(default=True, blank=False)
    audience_poll = models.BooleanField(default=False)
    positive = models.IntegerField(default = 4)
    negative = models.IntegerField(default = -2)
    objects = CustomUserManager()


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'teammate_one']

    def save(self, *args, **kwargs):
        if not self.team_id:
            self.team_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    # groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    # user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Mcq, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=(("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")))
    status = models.BooleanField(default=False)    
    submitted_at = models.DateTimeField(default = timezone.now)
    current_grading = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user_id) + " Question_no 👉 " + str(self.question_id) + " Selected_Option 👉 " + str(
            self.selected_option) + "  👉 " + str(self.status)


class StreakLifeline(models.Model):
    question = models.ForeignKey(Mcq, on_delete = models.CASCADE, default = 1)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(default = "NULL")
    conversion = models.CharField(default = "", max_length=300)

class SkipQuestionLifeline(models.Model):
    question = models.ForeignKey(Mcq, on_delete = models.CASCADE, default =1)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Message(models.Model):
    question = models.ForeignKey(Mcq, on_delete = models.CASCADE, default=1)
    user_id=models.ForeignKey(CustomUser,default=1, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_message} - {self.bot_message}"
   

from django.contrib.postgres.fields import JSONField

class AudiancePoll(models.Model):
    user = models.ForeignKey(CustomUser, on_delete= models.CASCADE)
    question = models.ForeignKey(Mcq, on_delete = models.CASCADE, default=1)
    poll = models.JSONField(default = {})
 # Import JSONField from postgres fields
