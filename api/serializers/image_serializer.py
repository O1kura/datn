from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from api.models.submission import Submission


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()


class ListSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        # exclude = ['init_data']
