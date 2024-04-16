# from django.shortcuts import redirect
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Mcq, Submission, CustomUser, StreakLifeline, SkipQuestionLifeline, Message, AudiancePoll
from .serializers import McqSerializer, McqEncodedSerializer, SubmissionSerializer, UserRegistrationSerializer, UserLoginSerializer, LeaderboardSerializer, MessageSerializer, AudiancePoll, StreakLifelineSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import timedelta, datetime
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
import random
from django.utils import timezone
from .Streak import function
# from rest_framework import generics
# import os
# from dotenv import load_dotenv
# import requests
# load_dotenv()
import google.generativeai as genai

pointer = 0

# arr= [str(os.getenv("GEMINI_KEY1")), str(os.getenv("GEMINI_KEY"))]

arr = ["AIzaSyCi7p8oBpIwtIcaOVFp2Lf925-ZxBUqcmo","AIzaSyDUK7hhkajiWBSNXeAv7E7sduozkXFwdwo"]


User = get_user_model()

POSTIVE_MARKS_1 = 4
POSTIVE_MARKS_2 = 2

NEGATIVE_MARKS_1 = -2
NEGATIVE_MARKS_2 = -1

SKIP_QUESTION_POSITIVE = 1
SKIP_QUESTION_NEGATIVE = -1


def if_end_time_exceeded(request):
    user = request.user
    if hasattr(user, 'end_time') and user.end_time < timezone.now():
        return True
    return False


# TODO @permission_classes([IsAuthenticated])
@api_view(['GET'])
def endpoints(request):
    available_endpoints = [
        '/endpoints/',
        '/token/refresh/',
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
        if not if_end_time_exceeded(request):
            ser = UserLoginSerializer(data=request.data)
            if ser.is_valid():
                username = ser.validated_data['username']
                password = ser.validated_data['password']
                user = authenticate(username=username, password=password, request=request)
                
                

                expiration_time = datetime.now() + timedelta(seconds=20)

                token_obj, _ = Token.objects.get_or_create(user=user)
                token_obj.expires_at = expiration_time
                token_obj.save()

                response = Response({'message': 'Login successful', "token": "token " + str(token_obj)}, status=status.HTTP_200_OK)
                response['Authorization'] = 'token ' + str(token_obj)
                return response
            else:
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_307_TEMPORARY_REDIRECT)

# ***** SKIP QUESTION LIFELINE *****
class SkipMcqView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not if_end_time_exceeded(request) and request.user.tab_switch <= 3 and not request.user.submitted:
            user = request.user
            token_obj, _ = Token.objects.get_or_create(user=user)
            
            user.positive = SKIP_QUESTION_POSITIVE
            user.negative = SKIP_QUESTION_NEGATIVE
            
            user.save()

            skip_object = SkipQuestionLifeline.objects.filter(user=user).first()
            
            mcq = Mcq.objects.get(question_id = user.current_question)
            

            if skip_object:
                if skip_object.question == mcq:
                    ser = McqSerializer(mcq)
                    response = Response(ser.data, status=status.HTTP_200_OK)
                    response['Authorization'] = 'token ' + str(token_obj)
                    return response
                else:
                    response = Response({"Error": "Lifeline not available or already used"}, status=status.HTTP_403_FORBIDDEN)
                    response['Authorization'] = 'token ' + str(token_obj)
                    return response
            # print(mcq, skip_object.question)
            if not skip_object:

                try:
                    questions_list_str = user.Questions_to_list
                    questions_list = questions_list_str.split(',')
                        
                        # Ensure questions are available
                    if not questions_list:
                        return Response({"Message": "Last question"}, status=status.HTTP_204_NO_CONTENT)

                        # Select a random question ID from the remaining questions
                    qid = random.choice(questions_list)
                    questions_list.remove(qid)
                        
                        # Update the user's remaining questions list
                    strs = ",".join(map(str, questions_list))
                    user.Questions_to_list = strs
                    user.current_question = qid
                    user.is_skip_question = False  # Set the lifeline flag to False indicating it's been used
                    user.save()

                        # Retrieve and serialize the selected question
                    mcq1 = Mcq.objects.get(question_id=qid, senior=user.senior_team)
                    ser = McqSerializer(mcq1)
                    skip_object = SkipQuestionLifeline.objects.create(user=user, question = mcq1)
                    skip_object.save()
                    response = Response(ser.data, status=status.HTTP_200_OK)
                    response['Authorization'] = 'token ' + str(token_obj)
                    return response
                except Exception as e:
                    return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"Error": "Lifeline not available or already used"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)


class GetCurrentQuestion(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if (not if_end_time_exceeded(request) or request.user.is_first_visit) and request.user.tab_switch <= 3 and not request.user.submitted:
            user = request.user
            token_obj, _ = Token.objects.get_or_create(user=user)
            try:
                if request.user.is_first_visit:
                    user.is_first_visit = False
                    # Set end_time for the first visit only
                    user.end_time = timezone.now() + timedelta(minutes=20)
                    user.save()

                # print(user.end_time)
                current_question_id = user.current_question
                if current_question_id:
                    try:
                        mcq = Mcq.objects.get(question_id=current_question_id, senior=user.senior_team)
                        ser = McqSerializer(mcq)
                        remaining_time = user.end_time - timezone.now()  # Calculate remaining time (using end_time
                        # print(remaining_time.seconds)
                        response = Response({"question_data": ser.data, "score": user.team_score, "username": user.username, "streak": user.question_streak, "time_remaining": remaining_time.seconds, "scheme": {"positive": user.positive, "negative": user.negative}, "token": str(token_obj)}, status=status.HTTP_200_OK)
                        response['Authorization'] = 'token ' + str(token_obj)
                        return response
                    except Mcq.DoesNotExist:
                        return Response({"Message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"Message": "No current question set"}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)

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
        if not if_end_time_exceeded(request) and request.user.tab_switch <= 3 and not request.user.submitted:
            try:

                user = request.user
                token_obj, _ = Token.objects.get_or_create(user=user)
                mcq = Mcq.objects.get(question_id=user.current_question)
                data = request.data
                selected = data.get("selected")

                status_of = False
                current_score = 0
        
                if str(mcq.correct) == selected:
                    user.team_score += user.positive
                    current_score += user.positive
                    user.previous_question = True
                    user.total_questions += 1
                    user.correct_questions += 1
                    status_of = True
                    mcq.total_responses += 1
                    mcq.correct_responses += 1
                    user.question_streak += 1

                else:
                    user.team_score += user.negative
                    current_score += user.negative
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
                    "current_grading": current_score,
                    "token": str(token_obj),
                }

                ser = SubmissionSerializer(data=payload_to_serializer)
                if ser.is_valid():
                    ser.save()
                    new_question_data = self.get_new_question_data(user, selected)
                    # ***** After clicking on submit button the submission will be saved and the new questions data will be sent as a response *****
                    if new_question_data is not None:
                        response = Response(new_question_data, status=status.HTTP_200_OK)
                        response['Authorization'] = 'token ' + str(token_obj)
                        return response
                    else:
                        return Response({"message": "question over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
                else:
                    return Response({"ERROR": "There was a problem, the serializer is not valid."})
            except Exception as e:
                print(f"Error during submission: {str(e)}")
                return Response({"ERROR": "There was a problem."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
                
                
            


    def get_new_question_data(self, user, selected):
        try:
            mcq = Mcq.objects.get(question_id=user.current_question)
            if str(mcq.correct) == selected:
                user.positive = POSTIVE_MARKS_1
                user.negative = NEGATIVE_MARKS_1
            else:
                user.positive = POSTIVE_MARKS_2
                user.negative = NEGATIVE_MARKS_2
            
            questions_list_str = user.Questions_to_list
            questions_list = questions_list_str.split(',')

            if not questions_list:
                return None  # No more questions available

            qid = questions_list[0]
            questions_list.remove(qid)
            strs = ",".join(map(str, questions_list))
            user.Questions_to_list = strs
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
            token_obj, _ = Token.objects.get_or_create(user=user)
            if user.total_questions != 0:
                accuracy = (user.correct_questions / user.total_questions) * 100
            else:
                accuracy = 0

            if user.senior_team == True:
                all_seniors = CustomUser.objects.filter(senior_team=True).order_by('-team_score') # Descending order
                team_rank = list(all_seniors).index(user) + 1 # First rank should be 1
            else:
                all_juniors = CustomUser.objects.filter(senior_team=False).order_by('-team_score') # Descending order
                team_rank = list(all_juniors).index(user) + 1
            
            result_page_data = {
                "username": user.username,
                "teammate_one": user.teammate_one,
                "team_rank": team_rank,
                "team_score": user.team_score,
                "total_questions": user.total_questions,
                "correct_questions": user.correct_questions,
                "user_accuracy": accuracy,
            }

            response = Response(result_page_data, status=status.HTTP_200_OK)
            response['Authorization'] = 'token ' + str(token_obj)
            return response
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


class EncodedDataView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):     
        
        if not if_end_time_exceeded(request) and request.user.tab_switch <= 3 and not request.user.submitted:
            user = request.user
            token_obj, _ = Token.objects.get_or_create(user=user)
            streak_lifeline = StreakLifeline.objects.filter(user=user).first()
            mcq = Mcq.objects.get(question_id = user.current_question)
            
            if streak_lifeline:
                if streak_lifeline.question == mcq:
                    ser = StreakLifelineSerializer(streak_lifeline, many = False)
                    
                    enc_data = {
                        "encoded_data": str(ser.data["message"]),
                        "from_to": str(ser.data["conversion"])
                    }
                    # print(enc_data)
                    return Response({"Encoded_data": enc_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": "Lifeline not available or already used"}, status=status.HTTP_403_FORBIDDEN)
            else:
                if int(user.question_streak) == 1:
                    li = []
                    li.append(user.current_question)
                    questions_list_str = user.Questions_to_list
                    questions_list = questions_list_str.split(',')
                    li.extend(questions_list[:1])

                    mcqs = Mcq.objects.filter(question_id__in=li)
                    serializer = McqEncodedSerializer(mcqs, many=True)
                    enc_data = function(serializer.data)
                    StreakLifeline.objects.create(user=user, question = mcq, message = str(enc_data["encoded_data"]), conversion = str(enc_data["from_to"]))
                    return Response({"Encoded_data": enc_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": "Lifeline not available or already used"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)

class RequestAudiencePollLifeline(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not if_end_time_exceeded(request) and request.user.tab_switch <= 3 and not request.user.submitted:
            try:
                user = request.user
                token_obj, _ = Token.objects.get_or_create(user=user)
                current_question_id = user.current_question
                mcq = Mcq.objects.get(question_id = current_question_id)
                audiancepoll = AudiancePoll.objects.filter(user = user).first()
                if audiancepoll:
                    if audiancepoll.question == mcq:
                        correct_answer_percentages = audiancepoll.poll
                        return Response({"correct_answer_percentages": correct_answer_percentages}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Audience poll already used."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    correct_answer_percentages = self.calculate_correct_answer_percentage(current_question_id)
                    audiancepoll = AudiancePoll.objects.create(user = user , question = mcq, poll = correct_answer_percentages)
                    user.audience_poll = True
                    user.save()
                    return Response({"correct_answer_percentages": correct_answer_percentages}, status=status.HTTP_200_OK)
                
            except Mcq.DoesNotExist:
                return Response({"message": "Question does not exist."}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({"message": "Internal server error.", "error": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)

    def calculate_correct_answer_percentage(self, current_question_id):
        try:
            all_submissions_for_question = Submission.objects.filter(question_id=current_question_id)
            total_submissions = all_submissions_for_question.count()

            if total_submissions == 0:
                mcq = Mcq.objects.get(question_id=current_question_id)
                mcq_ser = McqSerializer(mcq).data
                correct_option = mcq.correct.lower()
                rand_num1 = random.randint(50, 60)
                rand_num2 = 100 - rand_num1
                random_percentages = self.generate_random_percentages(rand_num1, rand_num2)
                percentage_options = {correct_option: float(rand_num1)}

                for option in ['a', 'b', 'c', 'd']:
                    if option != correct_option:
                        percentage_options[option] = float(random_percentages.pop())

                return percentage_options

            option_counts = all_submissions_for_question.values('selected_option').annotate(
                count=Count('selected_option'))
            option_count_dict = {option['selected_option']: option['count'] for option in option_counts}
            percentage_options = {}

            for option in ['a', 'b', 'c', 'd']:
                count = option_count_dict.get(option, 0)
                percentage = (count / total_submissions) * 100
                percentage_options[option] = percentage

            return percentage_options

        except Mcq.DoesNotExist:
            return Response({"message": "Question does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "Internal server error.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_random_percentages(self, num1, num2):
        rand_num3 = random.randint(1, num2)
        rand_num4 = random.randint(1, num2 - rand_num3)
        rand_num5 = num2 - rand_num3 - rand_num4
        return [rand_num3, rand_num4, rand_num5]


class ChatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not if_end_time_exceeded(request) and request.user.tab_switch <= 3 and not request.user.submitted:
            user= request.user
            token_obj, _ = Token.objects.get_or_create(user=user)
            mcq1 = Mcq.objects.filter(question_id=user.current_question).first()
            user_message = request.data.get('message')
            
            gpt = Message.objects.filter(user_id = user.team_id).first()
            
            if gpt:
                if gpt.question == mcq1:
                    ser = MessageSerializer(gpt, many=False)
                    return Response(ser.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Cannot access"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                bot_message = self.getgemini(user_message)
                payload_to_serializer = {
                        "user_id": user.team_id,
                        'user_message': user_message,
                        'bot_message': bot_message,
                        'question': mcq1.question_id
                        }
                serializer = MessageSerializer(data=payload_to_serializer)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
    def get(self, request):
        if not if_end_time_exceeded(request) and request.user.tab_switch <=3 and not request.user.submitted:
            user = request.user
            mcq1 = Mcq.objects.filter(question_id=user.current_question).first()
            gpt = Message.objects.filter(user_id = user.team_id).first()
            
            if gpt:
                if gpt.question == mcq1:
                    ser = MessageSerializer(gpt, many=False)
                    return Response(ser.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Cannot access"}, status=status.HTTP_400_BAD_REQUEST) 
            else:
                return Response({"message": "use the lifeline first"}, status=status.HTTP_400_BAD_REQUEST)           
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)      
        

    def getgemini(self, messg):
        global pointer
        # genai.configure(api_key=arr[pointer])
        genai.configure(api_key= "AIzaSyBWFXFRlzVnNQAtM9DZ5cFdfKPWSwi4GUI")

        pointer = (pointer+1)%len(arr)

        model = genai.GenerativeModel('gemini-pro')

        print(arr[0])

        response = model.generate_content(str(messg) + ". also, when you send the response dont use the ** or such operators."
                                                     "send a continuous string as response")
        # print(response.text)
        return response.text

    # def get_ai_response(self, user_input: str) -> str:
    #     # Set up the API endpoint and headers
    #     endpoint = "https://api.openai.com/v1/chat/completions"
    #     headers = {
    #         "Authorization": "Bearer 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",
    #         "Content-Type": "application/json",
    #     }
    #
    #     # Data payload
    #     messages = self.get_existing_messages()
    #     messages.append({"role": "user", "content": f"{user_input}"})
    #     data = {
    #         "model": "gpt-3.5-turbo",
    #         "messages": messages,
    #         "temperature": 0.7
    #     }
    #
    #     # Make the API request
    #     response = requests.post(endpoint, headers=headers, json=data)
    #     response_data = response.json()
    #
    #     # Check if there's an error in the response
    #     if 'error' in response_data:
    #         error_message = response_data['error']['message']
    #
    #         return f"Error: {error_message}"
    #
    #     # Check if 'choices' key exists in response_data
    #     if 'choices' in response_data:
    #         ai_message = response_data['choices'][0]['message']['content']
    #         return ai_message
    #     else:
    #         # Handle the case where 'choices' key is not present
    #         print("Unexpected response format from AI API")
    #         return "Error: Unexpected response format"
    # def get_existing_messages(self) -> list:
    #     """
    #     Get all messages from the database and format them for the API.
    #     """
    #     formatted_messages = []
    #
    #     for message in Message.objects.values('user_message', 'bot_message'):
    #         formatted_messages.append({"role": "user", "content": message['user_message']})
    #         formatted_messages.append({"role": "assistant", "content": message['bot_message']})
    #
    #     return formatted_messages
    

class AllLifelines(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        if not if_end_time_exceeded(request) and request.user.tab_switch <=3 and not request.user.submitted:
            user = request.user
            streak = StreakLifeline.objects.filter(user=user).first()
            audience = AudiancePoll.objects.filter(user=user).first()
            gpt = Message.objects.filter(user_id=user).first()
            skip = SkipQuestionLifeline.objects.filter(user=user).first()
            
            # print(gpt and gpt.question.question_id == user.current_question)
            # print(gpt.question.question_id == user.current_question)
            
            b1 = False
            b2 = False
            b3 = False
            if gpt:
                if gpt.question.question_id == user.current_question:
                    b1 = True
                else:
                    b1 = False
            else:
                b1 = False
            
            if audience:
                if audience.question.question_id == user.current_question:
                    b2 = True
                else:
                    b2 = False
            else:
                b2 = False

            if streak:
                if streak.question.question_id == user.current_question:
                    b3 = True
                else:
                    b3 = False
            else:
                b3 = False
            
            payload = {
                "used": {
                    "streak": streak is not None,
                    "audience": audience is not None,
                    "skip": skip is not None,
                    "gpt": gpt is not None,
                },
                "in_use": {
                    "streak": b3,
                    "audience": b2,
                    "gpt": b1,
                }
            }
            
            if skip:
                payload["used"]["skip"] = False
            
            return Response(payload, status=status.HTTP_200_OK)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)            
            
    

class TabSwitch(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not if_end_time_exceeded(request) and user.tab_switch <= 3 and not user.submitted:
            if request.data["bool"] == True:
                    user.tab_switch += 1
                    user.save()
                    return Response({"message": "Tab was switched!!!", "count": user.tab_switch}, status=status.HTTP_200_OK)                   
            else:
                return Response({"message": "Tab not switched", "count": user.tab_switch}, status=status.HTTP_200_OK)
        else:
            if if_end_time_exceeded(request):
                return Response({"message": "time over"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            else:
                return Response({"message": "submitted"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
