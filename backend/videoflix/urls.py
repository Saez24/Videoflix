"""
URL configuration for videoflix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import rq
from registration.api.views import VerifyEmailView
from django.urls import include
from profiles.api.views import PasswordResetRequestView, PasswordResetConfirmView
from django.urls import path

def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', include('login.api.urls')),
    path('api/registration/', include('registration.api.urls')),
    path('api/profiles/', include('profiles.api.urls')),
    path('api/content/', include('content.api.urls')),
    path('api/sub_profiles/', include('sub_profiles.api.urls')),
    path('api/registration/verify/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('django-rq/', include('django_rq.urls')), 
    path('rq/', include('django_rq.urls')),
    path('api/password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('api/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),  
    path('sentry-debug/', trigger_error),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
