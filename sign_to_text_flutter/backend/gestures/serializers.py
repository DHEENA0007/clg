"""
Serializers for the Gestures API
"""
from rest_framework import serializers
from .models import UserProfile, GestureSession, GestureData, GestureAccuracy, ASLSign


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = UserProfile
        fields = [
            'id', 'device_id', 'hand_size', 'dominant_hand',
            'total_gestures', 'average_accuracy', 'session_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_gestures', 'average_accuracy', 'session_count', 'created_at', 'updated_at']


class GestureDataSerializer(serializers.ModelSerializer):
    """Serializer for individual gesture data"""
    class Meta:
        model = GestureData
        fields = [
            'id', 'detected_sign', 'confidence', 'recognition_method',
            'landmarks', 'hand_shape', 'timestamp', 'is_low_confidence', 'recognition_failed'
        ]
        read_only_fields = ['id', 'timestamp']


class GestureSessionSerializer(serializers.ModelSerializer):
    """Serializer for gesture sessions with nested gestures"""
    gestures = GestureDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = GestureSession
        fields = [
            'id', 'session_context', 'started_at', 'ended_at',
            'gesture_count', 'average_confidence', 'gestures'
        ]
        read_only_fields = ['id', 'started_at', 'gesture_count', 'average_confidence']


class GestureAccuracySerializer(serializers.ModelSerializer):
    """Serializer for gesture accuracy data"""
    accuracy_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = GestureAccuracy
        fields = [
            'gesture_sign', 'attempts', 'successful', 'average_confidence',
            'personalized_threshold', 'accuracy_percentage', 'updated_at'
        ]
    
    def get_accuracy_percentage(self, obj):
        if obj.attempts > 0:
            return round(obj.successful / obj.attempts * 100, 1)
        return 0.0


class ASLSignSerializer(serializers.ModelSerializer):
    """Serializer for ASL sign reference"""
    class Meta:
        model = ASLSign
        fields = ['letter', 'description', 'hand_shape', 'emoji', 'image_url']


class GestureBatchSerializer(serializers.Serializer):
    """Serializer for batch gesture upload"""
    session_id = serializers.CharField(required=False, allow_null=True)
    user_id = serializers.CharField(required=True)
    gestures = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    user_profile = serializers.DictField(required=False, allow_null=True)
    is_retry = serializers.BooleanField(default=False)


class SignDetectionRequestSerializer(serializers.Serializer):
    """Serializer for sign detection request from camera frame"""
    landmarks = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        ),
        required=True
    )
    user_id = serializers.CharField(required=False, allow_null=True)
    session_context = serializers.CharField(default='camera_view')


class SignDetectionResponseSerializer(serializers.Serializer):
    """Serializer for sign detection response"""
    sign = serializers.CharField()
    confidence = serializers.FloatField()
    hand_shape = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    emoji = serializers.CharField(allow_null=True)
