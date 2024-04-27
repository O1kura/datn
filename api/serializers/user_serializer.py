from rest_framework import serializers

from api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        read_only_fields = ('email', 'username', 'is_superuser', 'date_joined', 'last_login', 'is_staff', 'is_active',
                            'groups', 'deleted_at')
