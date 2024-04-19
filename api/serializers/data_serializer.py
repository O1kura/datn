from rest_framework import serializers

from api.models.submission import Data, QuestionData


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        exclude = ['deleted_at']


class QuestionDataSerializer(serializers.ModelSerializer):
    # data = DataSerializer()

    class Meta:
        model = QuestionData
        exclude = ['deleted_at', 'question']

    # def validate(self, data):
    #     question = data.get('question')  # Assuming you have a ForeignKey to Question
    #     if not question.question_data_set.filter(category).exists():
    #         raise serializers.ValidationError("At least one correct answer must be associated with this question.")
    #     return data
