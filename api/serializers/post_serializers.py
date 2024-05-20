from rest_framework import serializers

from api.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ['img_path']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['tags'] = [str(tag) for tag in instance.tags.all()]

        return rep
