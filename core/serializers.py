from rest_framework import serializers
from .models import Mcq, Submission, CustomUser, StreakLifeline, Message, AudiancePoll
import random

class McqEncodedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mcq
        fields = [ 'question_id', 'question_md', 'a', 'b', 'c', 'd', 'correct', 'author', 'senior']

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
    team_score = serializers.SerializerMethodField()
    team_rank = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['username', 'team_rank', 'team_score', 'total_questions', 'correct_questions']
    
    def get_team_score(self, obj):
        return obj.max_streak + obj.team_score
    
    def get_team_rank(self, obj):
        teams = CustomUser.objects.filter(senior_team=obj.senior_team).order_by('-team_score')
        team_rank = list(teams).index(obj) + 1
        return 1
    

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
        fields = ['username', 'password', 'teammate_one', 'teammate_two', 'senior_team']

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
    is_team = serializers.BooleanField()
    


class StreakLifelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakLifeline
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(write_only=True)  # Change to accept question_id as integer
    # question = serializers.PrimaryKeyRelatedField(queryset=Mcq.objects.all(), write_only=True)  # Make question write-only
    class Meta:
        model = Message
        fields = '__all__'


class AudiancePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudiancePoll
        fields = '__all__'

