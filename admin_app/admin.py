from django.contrib import admin
from content.tasks import convert_to_hls
from profiles.models import Profile
from sub_profiles.models import SubProfile
from content.models import Video
from django.utils.html import format_html
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django_rq.queues import get_queue
from django_rq.models import Queue
from django_rq.admin import QueueAdmin

# Proxy-Modelle erstellen
class ProfileProxy(Profile):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Benutzerprofil'
        verbose_name_plural = 'Benutzerprofile'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')


class SubProfileProxy(SubProfile):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Unterprofil'
        verbose_name_plural = 'Unterprofile'


class SubProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_profile', 'username',
                    'first_name', 'last_name', 'is_child')


class ContentProxy (Video):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created_at', 'thumbnail_preview', 'likes', 'dislikes', 'views', 'category')

    def delete_model(self, request, obj):
        """Stellt sicher, dass delete() aufgerufen wird und das Signal getriggert wird."""
        obj.delete()

    def delete_queryset(self, request, queryset):
        # Jede Instanz einzeln löschen, um delete() zu triggern
        with transaction.atomic():
            for obj in queryset:
                obj.delete()
        self.message_user(request, _("Videos wurden erfolgreich gelöscht."), messages.SUCCESS)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="100" style="border-radius: 8px;"/>', obj.thumbnail.url)
        return "Kein Thumbnail"
    
    thumbnail_preview.short_description = 'Thumbnail Vorschau'

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk  # Prüfen, ob es ein neues Objekt ist
        super().save_model(request, obj, form, change)
        
        # Wenn es ein neues Objekt ist, starte die Konvertierung manuell
        if is_new and obj.video_file:
            queue = get_queue('default')
            queue.enqueue(convert_to_hls, obj.video_file.path, obj.id, job_timeout=360, result_ttl=0) 
    


# Registrierung der Proxy-Modelle
admin.site.register(ProfileProxy, ProfileAdmin)
admin.site.register(SubProfileProxy, SubProfileAdmin)
admin.site.register(ContentProxy, ContentAdmin)
admin.site.register(Queue, QueueAdmin)



# Admin-Panel Einstellungen
admin.site.site_header = 'Videoflix Verwaltung'
admin.site.site_title = 'Admin-Panel'
admin.site.index_title = 'Willkommen im Coderr Verwaltungsbereich'
