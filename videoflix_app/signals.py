from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_rq import get_queue

from .models import Video
from .api.services import generate_hls_for_video, delete_hls_for_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created, **kwargs):
    """
    Automatically executed, when a video is uploaded. 
    If a video_file exists, a HLS will be created.
    """
    if instance.video_file:
        print(
            f"[SIGNAL] post_save for video {instance.id}, enqueue HLS job")
        queue = get_queue("default")
        queue.enqueue(generate_hls_for_video, instance.id)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs):
    """
    automatically executed when a video was deleted.
    The HLS-Dir will be deleted too.
    """
    print(f"[SIGNAL] post_delete for video {instance.id}, deleting HLS-Files.")
    delete_hls_for_video(instance.id)
