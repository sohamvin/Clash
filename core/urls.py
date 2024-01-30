# urls.py
from django.urls import path
from .views import endpoints, get_mcq, get_leaderboard, submit, UserRegistrationView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('endpoints/', endpoints),
    path('mcq/', get_mcq),
    path('leaderboard/', get_leaderboard),
    path('submit/', submit),
    path('login/', CustomTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('register/', UserRegistrationView.as_view()),

]
