from django.contrib import admin
from .models import Mcq,Submission, CustomUser, StreakLifeline, SkipQuestionLifeline

# LATEST COMMIT ON Dev_sujal

# Register your models here.
admin.site.register(StreakLifeline)
@admin.register(Mcq)
class ModelMcq(admin.ModelAdmin):
    list_display = ['question_id', 'correct', 'correct_responses', 'total_responses', 'senior', 'author']
# admin.site.register(Submission)
# admin.site.register(CustomToken)
@admin.register(Submission)
class ModelSubmission(admin.ModelAdmin):
    list_display = ['submission_id', 'user_id', 'selected_option', 'question_id', 'current_grading','submitted_at']

@admin.register(CustomUser)
class ModelCustomUser(admin.ModelAdmin):
    list_display = ['team_id', 'email', 'username', 'teammate_one', 'current_question', 'question_streak', 'team_score', 'senior_team', 'end_time']
# admin.site.register(User)
@admin.register(SkipQuestionLifeline)
class ModelSkipQuestion(admin.ModelAdmin):
    list_display = ['user']
