# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register-view'),
    path('login/', UserLoginView.as_view(), name='login-view'),
    path('skip_question/', SkipMcqView.as_view(), name='skip-question-view'),
    path('current_question/', GetCurrentQuestion.as_view(), name='current-question-view'),
    path('logout/', LogoutView.as_view(), name='logout-view'),
    path('submit/', SubmitView.as_view(), name='submission-view'),
    path('result_page/', ResultPageView.as_view(), name='result-view'),
    path('leaderboard/', leaderboardView.as_view(), name='leaderboard-view'),
    path('streak_lifeline/', EncodedDataView.as_view()),
]
