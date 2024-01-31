from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.db import models
import uuid
from rest_framework.authtoken.models import Token

class CustomToken(Token):
    expires_at = models.DateTimeField(null=True, blank=True)



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

    def __str__(self):
        return str(self.question_id)


class Custom_user(models.Model):
    username = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return str(self.username) + "👉" + str(self.current_question) + "🌟" + str(self.score)


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Custom_user, on_delete=models.CASCADE, blank=False)
    question_id = models.ForeignKey(Mcq, on_delete=models.CASCADE, blank=False)
    selected_option = models.CharField(max_length=255, blank=False)
    status = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return str(self.user_id) + " Question_no 👉 " + str(self.question_id) + " Selected_Option 👉 " + str(
            self.selected_option) + " 👉 " + str(self.status)



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
    teammate_one = models.CharField(max_length=300)
    teammate_two = models.CharField(max_length=300, blank=True)
    team_score = models.IntegerField(default=0)
    current_question = models.IntegerField(default=1, blank=False)
    previous_question = models.BooleanField(default=True, blank=False)
    senior_team= models.BooleanField(default=False)
    Questions_to_list = models.TextField(default="NOTHING")
    objects = CustomUserManager()


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'teammate_one']

    def save(self, *args, **kwargs):
        if not self.team_id:
            self.team_id = str(uuid.uuid4())

        super().save(*args, **kwargs)


