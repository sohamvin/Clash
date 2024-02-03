# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('mcq/', GetMCQ.as_view(), name='getmcq-view'),
    path('logout/', LogoutView.as_view()),
    path('submit/', SubmitView.as_view()),
    # path('abc/', ABCSubmissionCreateView.as_view()),
]
