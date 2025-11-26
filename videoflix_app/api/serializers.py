from rest_framework import serializers
from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Provides essential video metadata such as title, description, category and creation timestamp.
    """

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",

        ]

    def get_thumbnail_url(self, obj):
        """
        Returns the full URL for the thumbnail image.
        """

        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            url = obj.thumbnail.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
