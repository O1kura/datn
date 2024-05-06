import base64
from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from api.models.submission import Submission, Question, File, Category
from api.serializers.data_serializer import QuestionDataSerializer, DataSerializer


class ListSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        # exclude = ['init_data']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['files'] = [x.id for x in instance.file_set.all()]
        return rep


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['path', 'deleted_at', 'user']

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
        rep['question'] = data
        rep['question_data'] = QuestionDataSerializer(instance=question_data, many=True).data

        rep['tags'] = [str(tag) for tag in instance.tags.all()]

        return rep


class QuestionWithImageSerializer(QuestionSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        img = instance.get_content_image()
        base64_string = base64.b64encode(img).decode('utf-8')
        rep['image'] = base64_string
        return rep


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        data_set = instance.data_set.filter(deleted_at__isnull=True)
        res = DataSerializer(instance=data_set, many=True).data
        rep['data_Set'] = res
        question_set = instance.question_set.all()
        list_question = []
        for question in question_set:
            list_question.append({
                'question_id': question.id,
                'question_name': question.display_name
            })
        rep['questions'] = list_question
        rep['tags'] = [str(tag) for tag in instance.tags.all()]

        return rep
