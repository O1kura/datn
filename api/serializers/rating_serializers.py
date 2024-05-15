from rest_framework import serializers

from api.models.rating import Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "rating", "review"]

    # def create(self, validated_data):
