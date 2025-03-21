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
        queue.enqueue(convert_to_hls, instance.video_file.path, instance.id, job_timeout=360, result_ttl=0)

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
        print("auto_delete_file_on_delete triggered")
        if instance.video_file:
            print(f"Video file path: {instance.video_file.path}")
            if os.path.isfile(instance.video_file.path):
                os.remove(instance.video_file.path)
                print("Video file deleted")
                
        if instance.thumbnail:
            print(f"Thumbnail path: {instance.thumbnail.path}")
            if os.path.isfile(instance.thumbnail.path):
                os.remove(instance.thumbnail.path)
                print("Thumbnail deleted")
