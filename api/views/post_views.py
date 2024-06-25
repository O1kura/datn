import json
import os

from django.http import HttpResponse
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models import User
from api.models.notification import Notification, NotificationType
from api.models.post import Post, LikePost, FollowersCount, Comment
from api.models.rating import Rating
from api.serializers.post_serializers import PostSerializer, CommentSerializer
from api.serializers.rating_serializers import RatingSerializer
from api.utils.utils import try_parse_datetime, update_tags, save_file


class ListPostView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        params = self.request.query_params
        title = params.get('title', None)
        tags = params.getlist('tags', None)
        start = params.get('from', None)
        end = params.get('to', None)

        start = try_parse_datetime(start)
        end = try_parse_datetime(end)

        post = Post.objects.all()
        if title:
            post = post.filter(title__icontains=title)
        if start:
            post = post.filter(created_at__gte=start)
        if end:
            post = post.filter(created_at__lte=end)
        if tags:
            if not isinstance(tags, list):
                tags = [tags]
            post = post.filter(tags__tag_name__in=tags)

        return post.order_by('-created_at')


class PostDetailView(GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('does_not_exists', label='post')

        res = PostSerializer(instance=post).data
        return Response(res)

    def put(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('does_not_exists', label='post')

        if post.author != request.user:
            raise CustomException('permission_denied', 'Not your posts')

        data = json.loads(request.body)
        file = request.FILES.get('file')
        if file:
            if post.img_path is not None and os.path.exists(post.img_path) and post.question:
                os.remove(post.img_path)
            path = save_file('posts', file)
            post.img_path = path

        tags = data.get('tags', None)
        del data['tags']

        if isinstance(tags, list):
            tags_model = update_tags(tags)
            post.tags.set(tags_model)

        post.save()

        serializer = PostSerializer(instance=post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('does_not_exists', label='post')

        if post.author != request.user:
            raise CustomException('permission_denied', 'Not your posts')

        post.delete()
        return Response({'status': 'OK'})


class PostImageView(GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('does_not_exists', label='post')

        return post.get_content_image()

    def put(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('does_not_exists', label='post')

        if post.author != request.user:
            raise CustomException('permission_denied', 'Not your posts')

        file = request.FILES.get('file')
        if file:
            if post.img_path is not None and os.path.exists(post.img_path) and not post.question:
                os.remove(post.img_path)
            path = save_file('posts', file)
            post.img_path = path
            post.save()

        return Response({"status": "ok"})


class LikePostView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_exists', label='post')

        like_filter = LikePost.objects.filter(post_id=post_id, user_id=user.id).first()

        if like_filter:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1
            post.save()
        else:
            new_like = LikePost.objects.create(post=post, user=user)
            new_like.save()
            post.no_of_likes = post.no_of_likes + 1
            post.save()

        data = PostSerializer(instance=post).data
        return Response(data)


class RateQuestionFromPostView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_exists', label='post')

        if not post.question:
            raise CustomException('does_not_exists', label='question')

        data = json.loads(request.body)

        rating, created = Rating.objects.get_or_create(user=user, question=post.question)

        serializer = RatingSerializer(instance=rating, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class FollowUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        following_user = User.objects.filter(id=user_id).first()
        if not following_user:
            raise CustomException("does_not_exists", label='user')
        follower = request.user
        if follower == following_user:
            raise CustomException("follow_conflict", message="Cant follow yourself")
        follower_count_obj = FollowersCount.objects.filter(follower=follower, following=following_user).first()
        if follower_count_obj:
            follower_count_obj.delete()
            notification = Notification.objects.filter(recepient=following_user, actor=request.user,
                                        type=NotificationType.get_followed.value).first()
            if notification:
                notification.delete()

            action = 'unfollow'
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=following_user)
            new_follower.save()
            action = 'follow'
            # for follower in question.user.follower.filter(is_active=True):
            message = f'{request.user.username} starts following you'
            notification = Notification(recepient=following_user, actor=request.user,
                                        type=NotificationType.get_followed.value,
                                        message=message)
            notification.save()
        return Response({'action': action})


class MakeCommentPost(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_exists', label='post')

        data = json.loads(request.body)

        cmt = Comment(author=user, post=post, body=data.get('text', ''))
        cmt.save()

        message = f'{user.username} makes a comment on post {post.title}'
        notification = Notification(recepient=post.author, actor=user,
                                    type=NotificationType.new_comment.value,
                                    message=message, post=post)
        notification.save()

        serializer = PostSerializer(instance=post)

        return Response(serializer.data)


class CommentPostView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id, comment_id):
        user = request.user
        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_exists', label='post')

        comment = post.comments.filter(id=comment_id, author=user).first()
        if not comment:
            raise CustomException('does_not_exists', label='comment')

        data = json.loads(request.body)

        comment.body = data.get('text', '')
        comment.save()

        return Response(CommentSerializer(instance=comment).data)

    def delete(self, request, post_id, comment_id):
        user = request.user
        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_exists', label='post')

        comment = post.comments.filter(id=comment_id, author=user).first()
        if not comment:
            raise CustomException('does_not_exists', label='comment')

        comment.delete()

        return Response({'status': 'ok'})
