import os

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from django.http import HttpResponse, FileResponse

from ..models import Video
from .services import HLS_RESOLUTIONS
from .serializers import VideoSerializer


class VideoListAPIView(generics.ListAPIView):
    """
    Get /api/video/
    Retrieves a list of all available videos.
    User needs to be authenticated
    """

    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        gives the request context to the serializer to build full URLs for thumbnails
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class VideoStreamManifestAPIView(APIView):
    """
    GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8
    Returns the HLS manifest file for the specified video and resolution.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        if resolution not in HLS_RESOLUTIONS:
            return Response({'detail': 'Resolution not found'}, status=404)

        try:
            video = Video.objects.get(pk=movie_id)
        except Video.DoesNotExist:
            return Response({'detail': 'Video not found'}, status=404)

        m3u8_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(
            video.id), resolution, 'index.m3u8')

        if not os.path.exists(m3u8_path):
            if not video.video_file:
                return Response(
                    {"detail": "No video file for this movie"},
                    status=404,
                )
            return Response(
                {"detail": "HLS stream is still being generated."},
                status=503,
            )

        with open(m3u8_path, 'r') as f:
            content = f.read()

        lines = content.splitlines()
        new_lines = []
        base_url = request.build_absolute_uri(
            f"/api/video/{video.id}/{resolution}/")

        for line in lines:
            if line.startswith('#') or not line.strip():
                new_lines.append(line)
            else:
                new_lines.append(base_url + line.strip())
        rewritten_content = '\n'.join(new_lines) + '\n'

        return HttpResponse(rewritten_content, content_type='application/vnd.apple.mpegurl',)


class VideoSegmentAPIView(APIView):
    """
    GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/
    Retrieves a single TS-segment for the HLS-video.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        if resolution not in HLS_RESOLUTIONS:
            return Response({"detail": "Resolution not found."}, status=404)

        if "/" in segment or ".." in segment:
            return Response({"detail": "Invalid segment name"}, status=404)
        try:
            video = Video.objects.get(pk=movie_id)
        except Video.DoesNotExist:
            return Response({"detail": "Video not found"}, status=404)

        segment_path = os.path.join(
            settings.MEDIA_ROOT, 'hls', str(video.id), resolution, segment)
        if not os.path.exists(segment_path):
            return Response({"detail": "Segment not found."}, status=404)

        return FileResponse(open(segment_path, 'rb'), content_type="video/MP2T",)
