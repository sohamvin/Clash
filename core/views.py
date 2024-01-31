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

senior_objs = Mcq.objects.filter(senior=True)
junior_objs = Mcq.objects.filter(senior=False)

seniorlist = []
juniorlist = []

# Process senior objects
for senior_obj in senior_objs:
    # Add your processing logic for senior objects
    seniorlist.append(senior_obj.question_id)

# Process junior objects
for junior_obj in junior_objs:
    # Add your processing logic for junior objects
    juniorlist.append(junior_obj.question_id)



random_number = random.randint(1, 10)

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
            username = ser.validated_data['username']
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
        current_id = user.current_question
        try:
            seni = user.senior_team

            qid = 0

            if seni:
                if seniorlist:
                    qid = random.choice(seniorlist)
                    seniorlist.remove(qid)
                else:
                    qid=-1
            else:
                if juniorlist:
                    qid = random.choice(juniorlist)
                    juniorlist.remove(qid)
                else:
                    qid = -1

            if qid == -1:
                return Response({"Messege": "Reached End of questions"}, status=status.HTTP_204_NO_CONTENT)
            mcq = Mcq.objects.get(question_id=qid, senior=user.senior_team)
            ser = Mcq_Serializer(mcq)
            return Response(ser.data, status=status.HTTP_200_OK)
        except:
            return Response({"Error": "Connot request question of not your catagory"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user associated with the token
        user = request.user

        # Delete the existing token for the user
        Token.objects.filter(user=user).delete()

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


