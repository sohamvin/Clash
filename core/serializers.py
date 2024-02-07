from rest_framework import serializers
from .models import Mcq, Submission, CustomUser



class McqSerializer(serializers.ModelSerializer):
    correct = serializers.CharField(write_only = True)

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

        if validated_data['senior_team']:
            senior_objs = Mcq.objects.filter(senior=True)
            seniorlist = [senior_obj.question_id for senior_obj in senior_objs]
            strs = ",".join(map(str, seniorlist))
            instance.Questions_to_list = strs
        else:
            junior_objs = Mcq.objects.filter(senior=False)
            juniorlist = [junior_obj.question_id for junior_obj in junior_objs]
            strs = ",".join(map(str, juniorlist))
            instance.Questions_to_list = strs

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField()  # Add this line

