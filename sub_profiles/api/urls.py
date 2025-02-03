from django.urls import path
from .views import SubProfileView, SubProfileDetailView

urlpatterns = [
    path('', SubProfileView.as_view(), name='subprofiles'),
    path('<int:pk>/', SubProfileDetailView.as_view(), name='subprofiles-detail'),
    # path('adult/', ProfileAdultViewSets.as_view(), name='adult-list'),
    # path('child/', ProfileChildViewSets.as_view(), name='child-list'),
]
