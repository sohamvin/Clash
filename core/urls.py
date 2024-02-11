# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register-view'),
    path('login/', UserLoginView.as_view(), name='login-view'),
    # path('mcq/', GetMCQ.as_view(), name='getMCQ-view'),
    path('current_question/', GetCurrentQuestion.as_view(), name='getCurrentQuestion-view'),
    path('logout/', LogoutView.as_view(), name='logout-view'),
    path('submit/', SubmitView.as_view(), name='submission-view'),
    path('result_page/', ResultPageView.as_view(), name='result-view'),
    path('leaderboard/', leaderboardView.as_view(), name='leaderboard-view'),
    path('streak_lifeline/', SendOnlyTheNextN.as_view()),
    # path('abc/', ABCSubmissionCreateView.as_view()),
]
