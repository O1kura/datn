import json
import os

from django.contrib.auth import update_session_auth_hash
from rest_framework.generics import GenericAPIView
from rest_framework import permissions

from api.middlewares.custome_middleware import CustomException
from api.models import User
from api.serializers.user_serializer import UserSerializer
from rest_framework.response import Response

from api.utils.utils import save_profile_image, str_to_bool


class ChangePassword(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, request.user)
            status_code = 200
            res = UserSerializer(user)
        else:
            raise CustomException('incorrect_pass')

        return Response(res.data, status=status_code)


class CurrentUserView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = UserSerializer(instance=request.user).data
        return Response(data)

    def put(self, request):
        data = json.loads(request.body)
        user = request.user

        user_serializer = UserSerializer(instance=user, data=data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        data = user_serializer.data
        return Response(data)


class UserProfileImageView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        user = request.user
        if user.profile_path is not None and os.path.exists(user.profile_path):
            os.remove(user.profile_path)
        if user.thumb_profile_path is not None and os.path.exists(user.profile_path):
            os.remove(user.thumb_profile_path)

        save_profile_image('profile', file, user=user)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

    def get(self, request):
        get_thumb = request.GET.get('get_thumb', 'true')
        get_thumb = str_to_bool(get_thumb)
        user = request.user

        if get_thumb:
            if user.thumb_profile_path is not None:
                return user.get_thumb_photo()
            else:
                return Response({'image': None})

        if user.profile_path is not None:
            return user.get_photo()

        return Response({'image': None})


class GetUserProfileImageView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise CustomException('does_not_exists', label='user')
        if user.deleted_at is not None or user.thumb_profile_path is None:
            return Response({'image': None})

        return user.get_thumb_photo()
