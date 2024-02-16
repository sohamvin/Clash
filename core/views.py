from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Mcq, Submission, CustomUser, StreakLifeline
from .serializers import McqSerializer, SubmissionSerializer, UserRegistrationSerializer, UserLoginSerializer, LeaderboardSerializer, StreakLifelineSerializer, SpecialMcqSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import timedelta, datetime
from pytz import timezone, utc
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
import random
from django.contrib.sessions.models import Session
from math import ceil
from django.utils import timezone
from .Streak import function

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

            return Response({"message": "Registration Succesful"}, status=status.HTTP_201_CREATED)
        return Response({"message": ser.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        ser = UserLoginSerializer(data=request.data)
        if ser.is_valid():
            username = ser.validated_data['username']
            password = ser.validated_data['password']
            user = authenticate(username=username, password=password, request=request)

            if user.senior_team:
                senior_objs = Mcq.objects.filter(senior=True)
                seniorlist = [senior_obj.question_id for senior_obj in senior_objs]
                random_question_id = random.choice(seniorlist)
                seniorlist.remove(random_question_id)
                user.current_question = random_question_id
                strs = ",".join(map(str, seniorlist))
                user.Questions_to_list = strs
            else:
                junior_objs = Mcq.objects.filter(senior=False)
                juniorlist = [junior_obj.question_id for junior_obj in junior_objs]
                random_question_id = random.choice(juniorlist)
                juniorlist.remove(random_question_id)
                user.current_question = random_question_id
                strs = ",".join(map(str, juniorlist))
                user.Questions_to_list = strs

            user.save()

            expiration_time = datetime.now() + timedelta(seconds=20)

            token_obj, _ = Token.objects.get_or_create(user=user)
            token_obj.expires_at = expiration_time
            token_obj.save()

            response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)

            response['Authorization'] = "token " + str(token_obj)

            return response
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# Will be called only one time, at the start of the contest (to set the first question as random)
# After submission, the get_new_question_data will be called from within the SubmitView, no need to redirect to this view
# class GetMCQ(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         token = request.auth
#         user = request.user

#         questions_list_str = user.Questions_to_list

#         questions_list = questions_list_str.split(',')
#         try:
#             if not questions_list:
#                 return Response({"Message": "Last question"}, status=status.HTTP_204_NO_CONTENT)

#             qid = random.choice(questions_list)
#             questions_list.remove(qid)
#             strs = ",".join(map(str, questions_list))
#             user.Questions_to_list = strs
#             user.current_question = qid
#             user.save()
#             mcq = Mcq.objects.get(question_id=qid, senior=user.senior_team)
#             ser = McqSerializer(mcq)
#             return Response(ser.data, status=status.HTTP_200_OK)
#         except:
#             return Response({"Error": "Ran out of questions"}, status=status.HTTP_400_BAD_REQUEST)


class GetCurrentQuestion(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Use Django's built-in flag for one-time checks
            if not request.user.end_time:
                # Set end_time for the first visit only
                user.end_time = timezone.now() + timedelta(minutes=30)
                user.save()  # Persist the saved end_time

            current_question_id = user.current_question
            if current_question_id:
                try:
                    mcq = Mcq.objects.get(question_id=current_question_id, senior=user.senior_team)
                    ser = McqSerializer(mcq)
                    remaining_time = user.end_time - timezone.now()  # Calculate remaining time (using end_time from user object)
                    return Response({
                        "Question_data": ser.data,
                        "Remaining_time": int(remaining_time.total_seconds())  # Convert to seconds if necessary
                    }, status=status.HTTP_200_OK)
                except Mcq.DoesNotExist:
                    return Response({"Message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"Message": "No current question set"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            mcq = Mcq.objects.get(question_id=user.current_question)
            data = request.data
            selected = data.get("selected")

            status_of = False
            current_score = 0

            if str(mcq.correct) == selected:
                if user.previous_question:
                    user.question_streak +=1
                    user.team_score += POSTIVE_MARKS_1
                    current_score += POSTIVE_MARKS_1
                else:
                    user.team_score += POSTIVE_MARKS_2
                    current_score += POSTIVE_MARKS_2
                user.previous_question = True
                user.total_questions += 1
                user.correct_questions += 1
                status_of = True
                mcq.total_responses += 1
                mcq.correct_responses += 1
                user.question_streak += 1

            else:
                if user.previous_question:
                    user.team_score += NEGATIVE_MARKS_1
                    current_score += NEGATIVE_MARKS_1
                else:
                    user.team_score += NEGATIVE_MARKS_2
                    current_score += NEGATIVE_MARKS_2
                user.previous_question = False
                user.total_questions += 1
                mcq.total_responses += 1
                user.question_streak = 0

            user.save()
            mcq.save()

            payload_to_serializer = {
                "user_id": user.team_id,
                "question_id": mcq.question_id,
                "selected_option": str(selected),
                "status": status_of,
                "current_grading": current_score
            }

            ser = SubmissionSerializer(data=payload_to_serializer)
            if ser.is_valid():
                ser.save()
                new_question_data = self.get_new_question_data(user)
                # ***** After clicking on submit button the submission will be saved and the new questions data will be sent as a response *****
                if new_question_data is not None:
                    return Response(new_question_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Ran out of questions"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"ERROR": "There was a problem, the serializer is not valid."})
        except Exception as e:
            print(f"Error during submission: {str(e)}")
            return Response({"ERROR": "There was a problem."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_new_question_data(self, user):
        try:
            # Attempt to get the streak lifeline for the user
            try:
                streak_lifeline = StreakLifeline.objects.get(user=user)
            except StreakLifeline.DoesNotExist:
                streak_lifeline = None

            if streak_lifeline is None:
                questions_list_str = user.Questions_to_list
                questions_list = questions_list_str.split(',')

                if not questions_list:
                    return None  # No more questions available

                qid = random.choice(questions_list)
                questions_list.remove(qid)
                strs = ",".join(map(str, questions_list))
                user.Questions_to_list = strs
                user.current_question = qid
                user.save()

            else:
                questions_list_str = streak_lifeline.questions
                questions_list = questions_list_str.split(',')

                if not questions_list:
                    streak_lifeline.delete()
                    return None  # No more questions available

                qid = random.choice(questions_list)
                questions_list.remove(qid)
                strs = ",".join(map(str, questions_list))
                streak_lifeline.questions = strs
                streak_lifeline.save()
                user.current_question = qid
                user.save()

            # Retrieve and serialize the new question
            mcq = Mcq.objects.get(question_id=qid, senior=user.senior_team)
            ser = McqSerializer(mcq)
            return ser.data

        except Mcq.DoesNotExist:
            return None  # Handle case where the retrieved MCQ does not exist

        except Exception as e:
            # Handle any other unexpected exceptions
            # Log the error or return a structured error response
            return None


class ResultPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            if user.total_questions != 0:
                accuracy = (user.correct_questions / user.total_questions) * 100
            else:
                accuracy = 0
            result_page_data = {
                "username": user.username,
                "teammate_one": user.teammate_one,
                "team_score": user.team_score,
                "total_questions": user.total_questions,
                "correct_questions": user.correct_questions,
                "user_accuracy": accuracy,
            }

            return Response(result_page_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class leaderboardView(APIView):
    def get(self, request):
        try:
            junior_list = CustomUser.objects.filter(senior_team=False, is_superuser=False).order_by('-team_score')  # Descending order
            senior_list = CustomUser.objects.filter(senior_team=True, is_superuser=False).order_by('-team_score')  # Descending order

            junior_list_serialized = LeaderboardSerializer(junior_list, many=True).data
            senior_list_serialized = LeaderboardSerializer(senior_list, many=True).data

            payload = {
                'junior_list': junior_list_serialized,
                'senior_list': senior_list_serialized,
            }

            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendOnlyTheNextN(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            token = request.auth
            user = request.user
            if user.question_streak != 1:
                return Response({"message": "Not on the streak"})


            payload = {
                "user": user.team_id
            }

            ser = StreakLifelineSerializer(data=payload)
            if ser.is_valid():
                instance = ser.save()

                listt = instance.questions.split(',')
                objs = []
                for l in listt:
                    objs.append(SpecialMcqSerializer(Mcq.objects.get(question_id=int(l))))

                datatosend = function(objs)

                return Response({"encoded": str(datatosend)}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Validation error", "errors": ser.errors}, status=400)

        except Exception as e:
            return Response({"message": str(e)}, status=500)

