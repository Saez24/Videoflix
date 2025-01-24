from django.urls import path
from .views import ContentViewSets

urlpatterns = [
    path('content/', ContentViewSets.as_view(), name='content-list'),
]