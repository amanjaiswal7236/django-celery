from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, AdminAnalyticsViewSet

router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')
router.register(r'admin/analytics', AdminAnalyticsViewSet, basename='admin-analytics')

urlpatterns = [
    path('', include(router.urls)),
]

