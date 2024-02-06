# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('mcq/', GetMCQ.as_view(), name='GetMCQ-view'),
    path('current_question/', GetCurrentQuestion.as_view(), name='GetCurrentQuestion-view'),
    path('logout/', LogoutView.as_view()),
    path('submit/', SubmitView.as_view()),
    path('result_page/', ResultPageView.as_view()),
    # path('abc/', ABCSubmissionCreateView.as_view()),
]
