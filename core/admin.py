from django.contrib import admin
from .models import Mcq,Submission, CustomUser, StreakLifeline, SkipQuestionLifeline, Message, AudiancePoll

# LATEST COMMIT ON Dev_sujal

# Register your models here.
@admin.register(StreakLifeline)
class ModelStreakLifeline(admin.ModelAdmin):
    list_display = ['user']

@admin.register(AudiancePoll)
class  ModelAudiencePoll(admin.ModelAdmin):
    list_display = ['user', 'question']

@admin.register(Mcq)
class ModelMcq(admin.ModelAdmin):
    search_fields = ['author', 'senior', 'total_responses', 'correct_responses']
    list_display = ['question_id', 'correct', 'correct_responses', 'total_responses', 'senior', 'author']
    ordering = ['senior','total_responses']
# admin.site.register(Submission)
# admin.site.register(CustomToken)
@admin.register(Submission)
class ModelSubmission(admin.ModelAdmin):
    search_fields = ['question_id', 'submitted_at', 'current_grading']
    list_display = ['submission_id', 'user_id', 'selected_option', 'question_id', 'current_grading','submitted_at']
    ordering = ['current_grading']
@admin.register(CustomUser)
class ModelCustomUser(admin.ModelAdmin):
    search_fields = ['team_id', 'email', 'current_question', 'team_score']
    list_display = ['team_id', 'email', 'username', 'teammate_one', 'current_question', 'question_streak', 'team_score', 'senior_team', 'end_time']
    ordering = ['team_score']
# admin.site.register(User)
@admin.register(SkipQuestionLifeline)
class ModelSkipQuestion(admin.ModelAdmin):
    list_display = ['user']

@admin.register(Message)
class Message(admin.ModelAdmin):
    list_display = ['user_id', 'user_message', 'bot_message']
