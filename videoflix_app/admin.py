from django.contrib import admin
from .models import Video
from .api.services import generate_hls_for_video

# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
