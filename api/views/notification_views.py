from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.serializers.notification_serializer import NotificationSerializer


class ReadNotificationsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, notification_id):
        notification = request.user.notifications.filter(id=notification_id).first()
        if not notification:
            raise CustomException("does_not_exists", label='notification')

        notification.is_read = True
        notification.save()

        return Response(NotificationSerializer(instance=notification).data)
