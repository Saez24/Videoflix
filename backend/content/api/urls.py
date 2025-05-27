from django.urls import path
from .views import ContentView
from .views import ContentViewPK


urlpatterns = [
    path('videos/', ContentView.as_view(), name='video_list'),
    path('videos/<int:pk>/', ContentViewPK.as_view(), name='video_detail'),
    # path('videos/delete/<int:video_id>/', VideoDeleteView.as_view(), name='video_delete'),
]