from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from api.models.submission import Submission, Question


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()


class ListSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields='__all__'
        # exclude = ['init_data']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
