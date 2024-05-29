from django.db.models import Sum, Count
from rest_framework import serializers

from api.models import User
from api.serializers.file_serializer import ListSubmissionSerializer


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'thumb_profile_path', 'profile_path']
        read_only_fields = ('email', 'username', 'is_superuser', 'date_joined', 'last_login', 'is_staff', 'is_active',
                            'groups', 'deleted_at')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['follower_count'] = len(instance.following_set.all())
        rep['following_count'] = len(instance.follower_set.all())

        return rep


class AdminUserSerializer(serializers.ModelSerializer):
    email = EmailSerializer

    class Meta:
        model = User
        exclude = ['password']
        read_only_fields = ('email', 'username')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['submissions_count'] = len(instance.submission_set.all())
        rep['total_file_sent'] = instance.submission_set.aggregate(total_file_sent=Sum('file_count'))['total_file_sent']

        total_file_count = 0
        for submision in instance.submission_set.all():
            total_file_count = total_file_count + submision.file_set.aggregate(total_file_count=Count('id'))['total_file_count']

        rep['total_file_count'] = total_file_count
        rep['submissions'] = ListSubmissionSerializer(instance=instance.submission_set.all(), many=True).data

        return rep
