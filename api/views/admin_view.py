from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import User
from api.models.post import Post, Comment
from api.models.submission import File, Data, Question, QuestionData
from api.serializers.data_serializer import DataSerializer, QuestionDataSerializer
from api.serializers.file_serializer import FileSerializer, QuestionSerializer, FileDetailSerializer
from api.serializers.post_serializers import PostSerializer, CommentSerializer
from api.serializers.user_serializer import UserSerializer, AdminUserSerializer


class AdminUserView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminFileView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = File.objects.all()
    serializer_class = FileDetailSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminDataView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = Data.objects.all()
    serializer_class = DataSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminQuestionView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminQuestionDataView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = QuestionData.objects.all()
    serializer_class = QuestionDataSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminCommentView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPostView(viewsets.ModelViewSet):
    """
       A simple ViewSet for viewing and editing accounts.
       """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAdminUser]

