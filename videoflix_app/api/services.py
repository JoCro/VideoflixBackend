import os
import shutil
import subprocess

from django.conf import settings
from django.db import connections
from django.apps import apps


HLS_RESOLUTIONS = {
    '480p': 480,
    '720p': 720,
    '1080p': 1080,
}

HLS_BITRATES = {
    '480p': '1000k',
    '720p': '2500k',
    '1080p': '5000k',
}


def generate_hls_for_video(video_id: int):
    """
    Runs in the background-worker(RQ). Fetches Videos from the DB and creates HLS-files.
    """
    Video = apps.get_model('videoflix_app', 'Video')
    video = Video.objects.get(pk=video_id)

    if not video.video_file:
        print(f"[HLS] Video {video.id} has no video_file")
        return

    input_path = video.video_file.path
    print(f"[HLS] Generating HLS for video {video.id}, Input: {input_path}")

    for resolution, height in HLS_RESOLUTIONS.items():
        output_dir = os.path.join(
            settings.MEDIA_ROOT, 'hls', str(video.id), resolution)
        os.makedirs(output_dir, exist_ok=True)
        output_playlist = os.path.join(output_dir, 'index.m3u8')
        segment_pattern = os.path.join(output_dir, 'segment_%03d.ts')

        video_bitrate = HLS_BITRATES.get(resolution, '2500k')

        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'h264',
            '-b:v', video_bitrate,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            output_playlist,
        ]
        print(
            f"[HLS] Running ffmpeg for {video.id} {resolution}: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"[HLS] OK: {output_playlist}")
        except subprocess.CalledProcessError as e:
            print(
                f"[HLS] FFmpeg failed for video {video.id} {resolution}: {e}")


def delete_hls_for_video(video_id: int):

    hls_root = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    if os.path.isdir(hls_root):
        shutil.rmtree(hls_root)
        print(f"[HLS] HLS-Directory for video {video_id} deleted: {hls_root}")
