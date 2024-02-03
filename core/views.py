from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Mcq, Submission, CustomUser
from .serializers import McqSerializer, SubmissionSerializer, UserRegistrationSerializer, UserLoginSerializer
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

            token_obj, _ = Token.objects.get_or_create(user=user)
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
            user.current_question = qid
            user.save()
            mcq = Mcq.objects.get(question_id=qid, senior=user.senior_team)
            ser = McqSerializer(mcq)
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




class SubmitView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.auth
            user = request.user
            # userinstance = CustomUser.objects.get(id=user.id)
            mcq = Mcq.objects.get(question_id=user.current_question)

            # payload_mcq = AllQuestionSerializer(mcq)
            # payload_mcq = payload_mcq.data
            #
            # payload_user = AllUserSerializer(userinstance)
            # payload_user = payload_user.data

            # return Response({"User": payload_mcq, "MCQ": payload_user})



            # in request will be only one feild for the current question: { "selected" : "a or b or c"} whatever the option the user selected
            data = request.data
            selected = data.get("selected")



            # POSTIVE_MARKS_1 = 4
            # POSTIVE_MARKS_2 = 2

            # NEGATIVE_MARKS_1 = -2
            # NEGATIVE_MARKS_2 = -1


            status_of = False

            if str(mcq.correct) == selected:
                if user.previous_question:
                    user.team_score += POSTIVE_MARKS_1
                else:
                    user.team_score += POSTIVE_MARKS_2
                user.previous_question = True
                status_of = True
                mcq.correct_responces += 1
            else:
                if user.previous_question:
                    user.team_score += NEGATIVE_MARKS_1
                else:
                    user.team_score += NEGATIVE_MARKS_2
                user.previous_question = False

            user.save()
            mcq.save()

            payload_to_serializer = {
                "user_id": user.team_id,
                "question_id":mcq.question_id,
                "selected_option":str(selected),
                "status": status_of
            }

            ser = SubmissionSerializer(data=payload_to_serializer)
            if ser.is_valid():
                ser.save()
                return Response({"messege": "Submitted"}, status=status.HTTP_200_OK)
            else:
                return Response({"ERROR" : "There was a problem"})
        except Exception as e:
            print(f"Error during submission: {str(e)}")
            return Response({"ERROR": "There was a problem"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ABCSubmissionCreateView(generics.CreateAPIView):
#     serializer_class = SubmissionSerializer

#     def create(self, request, *args, **kwargs):
#         user_id = request.data.get('user_id')  # Assuming you provide the user_id in the request data
#         question_id = request.data.get('question_id')  # Assuming you provide the question_id in the request data

#         try:
#             user = CustomUser.objects.get(id=user_id)
#             question = Mcq.objects.get(question_id=question_id)

#             # Validate if the user and question exist
#             if not user or not question:
#                 return Response({'error': 'Invalid user or question ID'}, status=status.HTTP_400_BAD_REQUEST)

#             # You can add more validation logic here if needed

#             # Create a Submission object
#             submission_data = {
#                 'user_id': user.id,
#                 'question_id': question.question_id,
#                 'selected_option': request.data.get('selected_option'),  # Assuming you provide selected_option in the request data
#                 'status': request.data.get('status', False),  # Assuming you provide status in the request data
#             }

#             serializer = ALLSubmissionSerializer(data=submission_data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except CustomUser.DoesNotExist or Mcq.DoesNotExist:
#             return Response({'error': 'User or question not found'}, status=status.HTTP_404_NOT_FOUND)



