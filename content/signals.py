import os
from django.db.models.signals import post_save, post_delete
from content.models import Video
from django.dispatch import receiver
import django_rq
from .tasks import convert_to_hls

print('Signals loaded')

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Sends variables to tasks.py to format through RQ Worker
    """
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_to_hls, instance.video_file.path, instance.id)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    print('Video post delete signal')
    if instance.video_file:
        if os.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)