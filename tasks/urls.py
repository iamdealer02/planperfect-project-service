from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

# Create a router instance
router = DefaultRouter()

# Register the TaskViewSet with the router
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # Include the router's URLs
    path('', include(router.urls)),

    # Additional paths for the API
    path('task/<str:pk>/create/', TaskViewSet.as_view({'post': 'create_task'}), name='create_task'),
    path('task/<str:pk>/tasks/', TaskViewSet.as_view({'get': 'list_tasks'}), name='list_tasks'),
    path('task/<str:pk>/tasks/<str:task_id>/', TaskViewSet.as_view({'get': 'view_task'}), name='view_task'),
    path('task/<str:pk>/tasks/<str:task_id>/update/', TaskViewSet.as_view({'patch': 'update_task'}), name='update_task'),
    path('task/<str:pk>/tasks/<str:task_id>/delete/', TaskViewSet.as_view({'delete': 'delete_task'}), name='delete_task'),
]
