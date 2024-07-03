from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet

# Initialize the router
# Default router here to create the URLs for the viewset
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
]
