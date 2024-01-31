from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Mcq, Custom_user, Submission, CustomUser, CustomToken
from .serializers import Mcq_Serializer, Submission_Serializer, UserRegistrationSerializer, UserLoginSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
import random

User = get_user_model()

POSTIVE_MARKS_1 = 4
POSTIVE_MARKS_2 = 2

NEGATIVE_MARKS_1 = -2
NEGATIVE_MARKS_2 = -1

# TODO @permission_classes([IsAuthenticated])

@api_view(['GET'])
def endpoints(request):
    available_endpoints = [
        '/endpoints/',
        '/mcq/',
        '/leaderboard/',
        '/submit/',
        '/login/',
        '/token/refresh/',
        '/register/',
        '/list-endpoints/',
    ]

    return JsonResponse({'available_endpoints': available_endpoints})

class UserRegistrationView(APIView):
    def post(self, request):
        ser = UserRegistrationSerializer(data=request.data)

        if ser.is_valid():
            ser.save()

            return Response({"messge": "Success"}, status=status.HTTP_201_CREATED)
        return Response({"messege": ser.errors}, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    def post(self, request):
        ser = UserLoginSerializer(data=request.data)
        if ser.is_valid():
            username = ser.validated_data['username']
            password = ser.validated_data['password']
            user = authenticate(username=username, password=password, request=request)

            expiration_time = timezone.now() + timedelta(seconds=20)

            token_obj, _ = CustomToken.objects.get_or_create(user=user)
            token_obj.expires_at = expiration_time
            token_obj.save()

            response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)

            response['Authorization'] = "token " + str(token_obj)

            return response
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class GetMCQ(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.auth
        user = request.user

        questions_list_str = user.Questions_to_list

        questions_list = questions_list_str.split(',')
        try:

            if not questions_list:
                return Response({"Messege": "Last question "}, status=status.HTTP_204_NO_CONTENT)


            qid = random.choice(questions_list)
            questions_list.remove(qid)
            strs = ",".join(map(str, questions_list))
            user.Questions_to_list = strs
            user.save()
            mcq = Mcq.objects.get(question_id=qid, senior=user.senior_team)
            ser = Mcq_Serializer(mcq)
            return Response(ser.data, status=status.HTTP_200_OK)
        except:
            return Response({"Error": "Ran out of questions"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user associated with the token
        user = request.user

        # Delete the existing token for the user
        Token.objects.filter(user=user).delete()

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


