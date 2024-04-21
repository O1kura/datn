import json

from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.submission import Question, Category, QuestionData
from api.serializers.data_serializer import QuestionDataSerializer
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
            raise CustomException('permission_denied', 'Not your questions')

        res = QuestionSerializer(instance=question).data
        return Response(res)

    def delete(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question.delete()
        return Response({'status': 'OK'})


class QuestionImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        image = question.get_content_image()
        return HttpResponse(image, content_type='image/JPEG')


class QuestionWithImageDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        res = QuestionWithImageSerializer(instance=question).data
        return Response(res)


class QuestionDataView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id, question_data_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('model_not_found', 'No question data found')

        res = QuestionDataSerializer(instance=question_data).data
        return Response(res)

    def put(self, request, question_id, question_data_id):
        data = json.loads(request.body)
        if 'data' in data:
            del data['data']

        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('model_not_found', 'No question data found')

        data_serializer = QuestionDataSerializer(instance=question_data, data=data, partial=True)
        data_serializer.is_valid(raise_exception=True)

        update_category = data.get('category', None)
        if update_category:
            if update_category == Category.cau_hoi.value:
                raise CustomException('question_error', 'Cant change the question category')
            # Phan loai cau hoi thi khong update loai
            if question_data.category == Category.cau_hoi.value:
                raise CustomException('question_error', 'Cant change the question category')
            # Phan loai dap an thi kiem tra xem co it nhat 1 dap an khac chua
            if question_data.category == Category.dap_an.value:
                question_ans = question.question_data_set.filter(category=Category.dap_an.value)
                if len(question_ans) == 1 and update_category != Category.dap_an.value:
                    raise CustomException('question_error', 'At least one correct answer for this question')

        data_serializer.save()
        res = data_serializer.data

        return Response(res)

    def delete(self, request, question_id, question_data_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('model_not_found', 'No question data found')

        category = question_data.category
        if category == Category.cau_hoi.value:
            raise CustomException('question_error', 'Cannot delete question type')
        if category in [Category.dap_an.value]:
            question_ans = question.question_data_set.filter(category=category)
            if len(question_ans) == 1:
                raise CustomException('question_error', 'At least one correct answer for this question')

        question_data.delete()
        return Response({'deleted_id': question_data_id})


class AddQuestionDataView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('model_not_found', 'No question found')

        if question.file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        data = json.loads(request.body)
        value = data.get('value', '')
        question_data = QuestionData(value=value, category=Category.cau_tra_loi.value, question=question)
        question_data.save()

        res = QuestionDataSerializer(instance=question_data).data
        return Response(res)
