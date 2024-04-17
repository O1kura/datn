from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.submission import Question
from api.serializers.image_serializer import QuestionSerializer, QuestionWithImageSerializer


class QuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        questions = Question.objects.filter(file__submission__user=user)
        res = QuestionSerializer(instance=questions, many=True).data

        return Response(res)


class QuestionDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('model_not_found', 'Not your questions')

        res = QuestionSerializer(instance=question).data
        return Response(res)

    def delete(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('model_not_found', 'Not your questions')

        question.delete()
        return Response({'status': 'OK'})


class QuestionImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('model_not_found', 'Not your questions')

        image = question.get_content_image()
        return HttpResponse(image, content_type='image/JPEG')


class QuestionWithImageDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('model_not_found', 'Not your questions')

        res = QuestionWithImageSerializer(instance=question).data
        return Response(res)
