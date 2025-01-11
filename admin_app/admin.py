from django.contrib import admin
from profiles.models import Profile


# Proxy-Modelle erstellen
class ProfileProxy(Profile):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Benutzerprofil'
        verbose_name_plural = 'Benutzerprofile'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'type')


# Registrierung der Proxy-Modelle
admin.site.register(ProfileProxy, ProfileAdmin)


# Admin-Panel Einstellungen
admin.site.site_header = 'Videoflix Verwaltung'
admin.site.site_title = 'Admin-Panel'
admin.site.index_title = 'Willkommen im Coderr Verwaltungsbereich'
