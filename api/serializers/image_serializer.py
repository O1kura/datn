import base64
from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from api.models.submission import Submission, Question, File, Category


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()


class ListSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        # exclude = ['init_data']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['path', 'deleted_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        data = {}
        question_data = instance.question_data_set

        question_q = question_data.filter(category=Category.cau_hoi.value)
        data['questions'] = [x.value for x in question_q]

        question_a = question_data.filter(category=Category.cau_tra_loi.value)
        data['answer'] = [x.value for x in question_a]

        question_c = question_data.filter(category=Category.dap_an.value)
        data['correct_answer'] = [x.value for x in question_c]
        # image = instance.get_content_image()
        # buf = None
        # base64.encode(image, buf)
        # rep['image'] = buf
        rep['question_data'] = data
        return rep


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
