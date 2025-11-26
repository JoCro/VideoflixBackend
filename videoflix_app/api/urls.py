from django.contrib import admin
from django.urls import path, include
from .views import VideoListAPIView, VideoStreamManifestAPIView, VideoSegmentAPIView

urlpatterns = [
    path('video/', VideoListAPIView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8',
         VideoStreamManifestAPIView.as_view(), name='video-stream',),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/',
         VideoSegmentAPIView.as_view(), name='video-segment',),
]
