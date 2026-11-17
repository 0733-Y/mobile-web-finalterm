from rest_framework import serializers

from .models import Post, Space


class PostSerializer(serializers.ModelSerializer):
    """Post 업로드(POST) / 목록·상세(GET) 공용."""

    class Meta:
        model = Post
        fields = ('id', 'author', 'space', 'title', 'text', 'image',
                  'person_count', 'level', 'created_date', 'published_date')
        read_only_fields = ('id', 'author', 'created_date')


class SpaceSerializer(serializers.ModelSerializer):
    """공간 + 최신 Post 요약."""
    latest = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = ('id', 'name', 'building', 'floor', 'capacity', 'has_outlet', 'latest')

    def get_latest(self, obj):
        post = obj.posts.filter(published_date__isnull=False).order_by(
            '-published_date', '-id').first()
        if post is None:
            return None
        request = self.context.get('request')
        image_url = None
        if post.image:
            image_url = request.build_absolute_uri(post.image.url) if request else post.image.url
        return {
            'post_id': post.id,
            'person_count': post.person_count,
            'level': post.level,
            'image': image_url,
            'published_date': post.published_date,
        }
