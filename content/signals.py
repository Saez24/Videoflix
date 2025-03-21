import os
from django.dispatch import receiver

from content.tasks import convert, delete_video_folder, delete_thumbnail_folder
from .models import Video
from django.db.models.signals import post_save, post_delete
import django_rq


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    This function queues the creation of the HLS files to a rq-worker.
    """
    if created:
        queue = django_rq.get_queue("default", autocommit=True)
        queue.enqueue(
            convert,
            instance.video_file.path,
            instance.title,
        )


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    This starts the deletion of the video folder.
    """
    if instance.video_file:
        base_folder = os.path.join("media", "videos", instance.title.replace(" ", "_"))
        if os.path.exists(base_folder):
            delete_video_folder(base_folder)


@receiver(post_delete, sender=Video)
def thumbnail_post_delete(sender, instance, **kwargs):
    """
    This function starts the deletion of the thumbnail.
    """
    if instance.thumbnail:
        thumbnail_folder = os.path.dirname(instance.thumbnail.path)
        delete_thumbnail_folder(thumbnail_folder)