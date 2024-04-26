from rest_framework import serializers

from api.models.submission import Data, QuestionData, Category
from api.models.tag import Tag


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = '__all__'


class QuestionDataSerializer(serializers.ModelSerializer):
    # data = DataSerializer()

    class Meta:
        model = QuestionData
        exclude = ['deleted_at', 'question']
    # def validate(self, data):
    #     question = self.instance.question
    #     if not question.question_data_set.filter(category=Category.dap_an.value).exists():
    #         raise serializers.ValidationError("At least one correct answer must be associated with this question.")
    #     return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag