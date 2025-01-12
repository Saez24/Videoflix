from django.urls import path
from .views import ProfileViewSets, ProfileAdultViewSets, ProfileChildViewSets

urlpatterns = [
    path('<int:pk>/', ProfileViewSets.as_view(), name='profile-detail'),
    path('adult/', ProfileAdultViewSets.as_view(), name='adult-list'),
    path('child/', ProfileChildViewSets.as_view(), name='child-list'),
]
