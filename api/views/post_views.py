import json

from django.http import HttpResponse
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.post import Post, LikePost
from api.serializers.post_serializers import PostSerializer
from api.utils.utils import try_parse_datetime, update_tags


class ListPostView(ListAPIView):
    permission_classes = [IsAuthenticated]
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

        return post


class PostDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('model_not_found', 'No post found')

        res = PostSerializer(instance=post).data
        return Response(res)

    def put(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('model_not_found', 'No post found')

        if post.author != request.user:
            raise CustomException('permission_denied', 'Not your posts')

        data = json.loads(request.body)
        display_name = data.get('display_name', None)
        tags = data.get('tags', [])

        if isinstance(tags, list):
            tags_model = update_tags(tags)
            post.tags.set(tags_model)

        if display_name:
            post.display_name = display_name
            post.save()

        res = PostSerializer(instance=post).data
        return Response(res)

    def delete(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('model_not_found', 'No post found')

        if post.author != request.user:
            raise CustomException('permission_denied', 'Not your posts')

        post.delete()
        return Response({'status': 'OK'})


class PostImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            raise CustomException('model_not_found', 'No post found')

        return post.get_content_image()


class LikePostView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        post = Post.objects.filter(id=post_id).first()
        if not Post:
            raise CustomException('does_not_found', label='post')

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
