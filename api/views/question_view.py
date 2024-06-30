import json
import mimetypes

from django.db.models import Count, F
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.notification import Notification, NotificationType
from api.models.post import Post
from api.models.rating import Rating
from api.models.submission import Question, Category, QuestionData
from api.models.tag import Tag
from api.serializers.data_serializer import QuestionDataSerializer
from api.serializers.file_serializer import QuestionSerializer, QuestionWithImageSerializer
from api.serializers.post_serializers import PostSerializer
from api.serializers.rating_serializers import RatingSerializer
from api.utils.utils import update_tags, try_parse_datetime


class QuestionView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        display_name = params.get('display_name', None)
        tags = params.getlist('tags', None)
        start = params.get('from', None)
        end = params.get('to', None)

        start = try_parse_datetime(start)
        end = try_parse_datetime(end)

        question = Question.objects.filter(user=user)
        if display_name:
            question = question.filter(display_name__contains=display_name)
        if start:
            question = question.filter(created_at__gte=start)
        if end:
            question = question.filter(created_at__lte=end)
        if tags:
            if not isinstance(tags, list):
                tags = [tags]
            question = question.filter(tags__tag_name__in=tags)

        return question.order_by('-created_at')

    # def get(self, request):
    #     user = request.user
    #     questions = Question.objects.filter(file__submission__user=user)
    #     res = QuestionSerializer(instance=questions, many=True).data
    #
    #     return Response(res)


class QuestionDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        res = QuestionSerializer(instance=question).data
        return Response(res)

    def put(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        data = json.loads(request.body)
        display_name = data.get('display_name', None)
        tags = data.get('tags', [])

        if isinstance(tags, list):
            tags_model = update_tags(tags)
            question.tags.set(tags_model)

        if display_name:
            question.display_name = display_name
            question.save()

        res = QuestionSerializer(instance=question).data
        return Response(res)

    def delete(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question.delete()
        return Response({'status': 'OK'})


class QuestionImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        image = question.get_content_image()
        return HttpResponse(image, content_type='image/JPEG')


class QuestionWithImageDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        res = QuestionWithImageSerializer(instance=question).data
        return Response(res)


class QuestionDataView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id, question_data_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('does_not_exists', label='question data')

        res = QuestionDataSerializer(instance=question_data).data
        return Response(res)

    def put(self, request, question_id, question_data_id):
        data = json.loads(request.body)
        if 'data' in data:
            del data['data']

        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('does_not_exists', label='question_data')

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
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        question_data = question.question_data_set.filter(id=question_data_id).first()
        if not question_data:
            raise CustomException('does_not_exists', label='question data')

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
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        data = json.loads(request.body)
        value = data.get('value', '')
        question_data = QuestionData(value=value, category=Category.cau_tra_loi.value, question=question)
        question_data.save()

        res = QuestionDataSerializer(instance=question_data).data
        return Response(res)


class QUestionRatingView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        data = json.loads(request.body)

        rating, created = Rating.objects.get_or_create(user=request.user, question=question)

        serializer = RatingSerializer(instance=rating, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class QuestionShareView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        question = Question.objects.filter(id=question_id).first()
        if question is None:
            raise CustomException('does_not_exists', label='question')

        if question.user != request.user:
            raise CustomException('permission_denied', 'Not your questions')

        data = json.loads(request.body)
        caption = data.get('caption', '')
        title = data.get('title', '')
        post = Post(question=question, author=request.user, caption=caption, img_path=question.path, created_at=timezone.now(), title=title)
        post.save()
        post.tags.set(question.tags.all())
        post.save()

        message = f'{question.user.username} has a new post!'
        for follower_count in question.user.following_set.filter(follower__is_active=True):
            notification = Notification(recipient=follower_count.follower, actor=question.user, type=NotificationType.new_post.value,
                                        message=message, post=post)
            notification.save()

        serializer = PostSerializer(instance=post)

        return Response(serializer.data)
