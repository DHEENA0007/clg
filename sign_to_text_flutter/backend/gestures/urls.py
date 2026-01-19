"""
URL configuration for gestures API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserProfileViewSet, basename='user')
router.register(r'sessions', views.GestureSessionViewSet, basename='session')
router.register(r'signs', views.ASLSignViewSet, basename='sign')

urlpatterns = [
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health'),
    
    # Sign detection
    path('detect/', views.SignDetectionView.as_view(), name='detect-sign'),
    path('detect-image/', views.ImageDetectionView.as_view(), name='detect-image'),
    
    # Gesture data
    path('gestures/', views.GestureBatchView.as_view(), name='gestures-batch'),
    path('gestures/stats/<str:user_id>/', views.GestureStatsView.as_view(), name='gestures-stats'),
    path('gestures/thresholds/<str:user_id>/', views.PersonalizedThresholdsView.as_view(), name='gestures-thresholds'),
    
    # Admin
    path('admin/analytics/', views.AnalyticsView.as_view(), name='admin-analytics'),
    
    # Router URLs
    path('', include(router.urls)),
]
