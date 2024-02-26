from rest_framework import serializers
from .models import Mcq, Submission, CustomUser, StreakLifeline
import random


class McqSerializer(serializers.ModelSerializer):
    correct = serializers.CharField(write_only = True)

    class Meta:
        model = Mcq
        fields = [ 'question_id', 'question_md', 'a', 'b', 'c', 'd', 'correct', 'author', 'senior']

class SpecialMcqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mcq
        fields = [ 'question_id', 'question_md', 'a', 'b', 'c', 'd', 'correct', 'author', 'senior']


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'team_score', 'total_questions', 'correct_questions']


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


from rest_framework import serializers
from django.contrib.auth import get_user_model
import random

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['team_id', 'username', 'email', 'password', 'teammate_one', 'senior_team']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

            if instance.senior_team:
                senior_objs = Mcq.objects.filter(senior=True)
                seniorlist = [senior_obj.question_id for senior_obj in senior_objs]
                random.shuffle(seniorlist)
                random_question_id = random.choice(seniorlist)
                seniorlist.remove(random_question_id)
                instance.current_question = random_question_id
                strs = ",".join(map(str, seniorlist))
                instance.Questions_to_list = strs
            else:
                junior_objs = Mcq.objects.filter(senior=False)
                juniorlist = [junior_obj.question_id for junior_obj in junior_objs]
                random_question_id = random.choice(juniorlist)
                random.shuffle(juniorlist)
                juniorlist.remove(random_question_id)
                instance.current_question = random_question_id
                strs = ",".join(map(str, juniorlist))
                instance.Questions_to_list = strs

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField()
    


# class StreakLifelineSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StreakLifeline
#         fields = ['user']

#     def create(self, validated_data):
#         userr = validated_data.get('user')

#         # Check if userr is not None and Questions_to_list is not empty
#         if userr and userr.Questions_to_list:
#             listt = userr.Questions_to_list.split(",")
#             item = int(userr.current_question)
#             listt.append(item)

#             # Ensure that there are at least 5 items to select randomly
#             #should be 5, but 2 for testing purposes
#             if len(listt) >= 2:
#                 random_items = random.sample(listt, 2)
#                 my_list = [item for item in listt if item not in random_items]
#                 strs = ",".join(map(str, my_list))
#                 userr.Questions_to_list = strs

#                 abc = ",".join(map(str, random_items))
#                 instance = StreakLifeline.objects.create(questions=abc, user=userr, is_on=True)
#                 userr.current_question = random_items[0]
#                 userr.save()
#                 return instance
#             else:
#                 # Handle case where Questions_to_list has fewer than 5 items
#                 raise serializers.ValidationError("Questions_to_list should have at least 2 items.")
#         else:
#             # Handle case where userr is None or Questions_to_list is empty
#             raise serializers.ValidationError("Invalid user or empty Questions_to_list.")

