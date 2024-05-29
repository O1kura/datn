from rest_framework import serializers

from api.models.post import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ['img_path']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['comments'] = CommentSerializer(instace=instance.comments,many=True).data
        rep['tags'] = [str(tag) for tag in instance.tags.all()]

        return rep


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
