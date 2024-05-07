from rest_framework import serializers

from api.models import User
from api.serializers.file_serializer import ListSubmissionSerializer


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        read_only_fields = ('email', 'username', 'is_superuser', 'date_joined', 'last_login', 'is_staff', 'is_active',
                            'groups', 'deleted_at')


class AdminUserSerializer(serializers.ModelSerializer):
    email = EmailSerializer

    class Meta:
        model = User
        exclude = ['password']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['submissions'] = ListSubmissionSerializer(instance=instance.submission_set.all(), many=True).data
        return rep
