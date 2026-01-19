"""
Models for Sign Language to Text Conversion
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class UserProfile(models.Model):
    """Extended user profile for sign language preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    device_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    hand_size = models.CharField(max_length=20, choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], default='medium')
    dominant_hand = models.CharField(max_length=10, choices=[
        ('left', 'Left'),
        ('right', 'Right'),
    ], default='right')
    total_gestures = models.IntegerField(default=0)
    average_accuracy = models.FloatField(default=0.0)
    session_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Profile for {self.user.username}"
        return f"Profile {self.device_id}"


class GestureSession(models.Model):
    """A detection session containing multiple gestures"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sessions')
    session_context = models.CharField(max_length=50, default='general')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    gesture_count = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'gesture_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session {self.id} - {self.gesture_count} gestures"


class GestureData(models.Model):
    """Individual gesture detection data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GestureSession, on_delete=models.CASCADE, related_name='gestures', null=True, blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='gestures')
    
    # Detection data
    detected_sign = models.CharField(max_length=10)
    confidence = models.FloatField()
    recognition_method = models.CharField(max_length=50, default='fingerpose')
    
    # Landmark data (stored as JSON)
    landmarks = models.JSONField(null=True, blank=True)
    hand_shape = models.CharField(max_length=50, null=True, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_low_confidence = models.BooleanField(default=False)
    recognition_failed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'gesture_data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_profile', 'detected_sign']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.detected_sign} ({self.confidence:.2f})"


class GestureAccuracy(models.Model):
    """Tracks accuracy per gesture sign for a user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='accuracies')
    gesture_sign = models.CharField(max_length=10)
    attempts = models.IntegerField(default=0)
    successful = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    personalized_threshold = models.FloatField(default=0.8)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gesture_accuracy'
        unique_together = ['user_profile', 'gesture_sign']
        ordering = ['-successful']
    
    def __str__(self):
        accuracy = self.successful / self.attempts * 100 if self.attempts > 0 else 0
        return f"{self.gesture_sign}: {accuracy:.1f}%"


class ASLSign(models.Model):
    """Reference data for ASL signs"""
    letter = models.CharField(max_length=5, primary_key=True)
    description = models.TextField()
    hand_shape = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    
    class Meta:
        db_table = 'asl_signs'
        ordering = ['letter']
    
    def __str__(self):
        return f"ASL: {self.letter}"
