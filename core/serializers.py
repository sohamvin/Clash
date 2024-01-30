from rest_framework import serializers
from .models import Mcq, Custom_user, Submission, CustomUser




class Mcq_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Mcq
        fields = ['question_md', 'a', 'b', 'c', 'd', 'correct', 'author', 'senior']


# class Custom_user_Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Custom_user
#         fields = ['username', 'score', 'current_question', 'previous_question']


class Submission_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['submission_id', 'user_id', 'question_id', 'selected_option', 'status']


from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'teammate_one', 'senior_team']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance



