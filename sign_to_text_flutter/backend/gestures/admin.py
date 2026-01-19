from django.contrib import admin
from .models import UserProfile, GestureSession, GestureData, GestureAccuracy, ASLSign


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'device_id', 'hand_size', 'dominant_hand', 'total_gestures', 'session_count', 'created_at']
    list_filter = ['hand_size', 'dominant_hand']
    search_fields = ['device_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(GestureSession)
class GestureSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_profile', 'session_context', 'gesture_count', 'average_confidence', 'started_at']
    list_filter = ['session_context', 'started_at']
    search_fields = ['user_profile__device_id']
    readonly_fields = ['id', 'started_at']


@admin.register(GestureData)
class GestureDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_profile', 'detected_sign', 'confidence', 'recognition_method', 'timestamp']
    list_filter = ['detected_sign', 'recognition_method', 'is_low_confidence']
    search_fields = ['detected_sign', 'user_profile__device_id']
    readonly_fields = ['id', 'timestamp']


@admin.register(GestureAccuracy)
class GestureAccuracyAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'gesture_sign', 'attempts', 'successful', 'average_confidence', 'updated_at']
    list_filter = ['gesture_sign']
    search_fields = ['user_profile__device_id', 'gesture_sign']


@admin.register(ASLSign)
class ASLSignAdmin(admin.ModelAdmin):
    list_display = ['letter', 'description', 'hand_shape', 'emoji']
    search_fields = ['letter', 'description']
