from django.contrib import admin
from profiles.models import Profile
from sub_profiles.models import SubProfile


# Proxy-Modelle erstellen
class ProfileProxy(Profile):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Benutzerprofil'
        verbose_name_plural = 'Benutzerprofile'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'is_active', 'is_verified', 'subscription_model')


class SubProfileProxy(SubProfile):
    class Meta:
        proxy = True
        app_label = 'admin_app'
        verbose_name = 'Unterprofil'
        verbose_name_plural = 'Unterprofile'


class SubProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_profile', 'username',
                    'first_name', 'last_name', 'is_child')


# Registrierung der Proxy-Modelle
admin.site.register(ProfileProxy, ProfileAdmin)
admin.site.register(SubProfileProxy, SubProfileAdmin)


# Admin-Panel Einstellungen
admin.site.site_header = 'Videoflix Verwaltung'
admin.site.site_title = 'Admin-Panel'
admin.site.index_title = 'Willkommen im Coderr Verwaltungsbereich'
