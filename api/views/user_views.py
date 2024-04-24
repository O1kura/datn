import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView
from rest_framework import permissions

from api.middlewares.custome_middleware import CustomException
from api.serializers.user_serializer import UserSerializer
from rest_framework.response import Response


class UserView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        data = UserSerializer(instance=users, many=True).data
        return Response(data=data)


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
