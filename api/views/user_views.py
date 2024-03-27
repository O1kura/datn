from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from api.serializers.user_serializer import UserSerializer
from rest_framework.response import Response


class UserView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        data = UserSerializer(instance=users, many=True).data
        return Response(data=data)
