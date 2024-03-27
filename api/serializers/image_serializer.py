from rest_framework import serializers


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
