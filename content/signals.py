import os
from django.db.models.signals import post_save, post_delete
from content.models import Video
from django.dispatch import receiver
import django_rq
from .tasks import QUALITIES, convert_to_hls, create_base_directory, convert_single_quality, finalize_hls_conversion

print('Signals loaded')

# In signals.py
@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default')
        base_name = create_base_directory(instance.video_file.path)
        
        # Enqueue each quality conversion as a separate job
        jobs = []  # Collect job objects
        for quality, (resolution, bitrate) in QUALITIES.items():
            job = queue.enqueue(
                convert_single_quality, 
                instance.video_file.path, 
                base_name, 
                quality, 
                resolution, 
                bitrate, 
                instance.id,
                job_timeout=760,
                result_ttl=0                
            )
            jobs.append(job)  # Add the job to the list
        
        # Enqueue a job to create the master playlist after all conversions
        queue.enqueue(
            finalize_hls_conversion,
            instance.video_file.path,
            instance.id,
            depends_on=jobs,  # Use the collected jobs
            job_timeout=60
        )

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
