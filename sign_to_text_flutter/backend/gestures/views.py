"""
Views for Sign Language to Text API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Sum, Count
from django.utils import timezone
import uuid
import logging

from .models import UserProfile, GestureSession, GestureData, GestureAccuracy, ASLSign
from .serializers import (
    UserProfileSerializer, GestureSessionSerializer, GestureDataSerializer,
    GestureAccuracySerializer, ASLSignSerializer, GestureBatchSerializer,
    SignDetectionRequestSerializer, SignDetectionResponseSerializer
)
from .sign_detector import detect_sign, ASL_DESCRIPTIONS, HAND_SHAPES

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """API health check endpoint"""
    
    def get(self, request):
        return Response({
            'status': 'OK',
            'message': 'Sign Language to Text API is running',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat()
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """Manage user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    @action(detail=False, methods=['post'])
    def get_or_create_by_device(self, request):
        """Get or create user profile by device ID"""
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'error': 'device_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile, created = UserProfile.objects.get_or_create(
            device_id=device_id,
            defaults={
                'hand_size': request.data.get('hand_size', 'medium'),
                'dominant_hand': request.data.get('dominant_hand', 'right')
            }
        )
        
        serializer = self.get_serializer(profile)
        return Response({
            'profile': serializer.data,
            'created': created
        })


class GestureSessionViewSet(viewsets.ModelViewSet):
    """Manage gesture detection sessions"""
    queryset = GestureSession.objects.all()
    serializer_class = GestureSessionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_profile_id=user_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """Mark a session as ended"""
        session = self.get_object()
        session.ended_at = timezone.now()
        
        # Calculate session stats
        gestures = session.gestures.all()
        session.gesture_count = gestures.count()
        if session.gesture_count > 0:
            session.average_confidence = gestures.aggregate(
                avg=Avg('confidence')
            )['avg'] or 0.0
        
        session.save()
        serializer = self.get_serializer(session)
        return Response(serializer.data)


class SignDetectionView(APIView):
    """Real-time sign detection from landmarks"""
    
    def post(self, request):
        """
        Detect sign language from hand landmarks.
        
        Expected input:
        {
            "landmarks": [[x, y, z], [x, y, z], ...],  // 21 landmarks
            "user_id": "optional-user-id",
            "session_context": "camera_view"
        }
        """
        serializer = SignDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        landmarks = serializer.validated_data['landmarks']
        user_id = serializer.validated_data.get('user_id')
        session_context = serializer.validated_data.get('session_context', 'api')
        
        # Detect sign
        result = detect_sign(landmarks)
        
        if not result:
            return Response({
                'detected': False,
                'message': 'No hand gesture detected'
            })
        
        # Optionally save gesture data
        if user_id:
            try:
                profile = UserProfile.objects.get(id=user_id)
                GestureData.objects.create(
                    user_profile=profile,
                    detected_sign=result.sign,
                    confidence=result.confidence,
                    recognition_method='api_detection',
                    landmarks=landmarks,
                    hand_shape=result.hand_shape,
                    is_low_confidence=result.confidence < 0.7
                )
                
                # Update accuracy stats
                self._update_accuracy(profile, result.sign, result.confidence)
                
            except UserProfile.DoesNotExist:
                pass
        
        return Response({
            'detected': True,
            'sign': result.sign,
            'confidence': result.confidence,
            'hand_shape': result.hand_shape,
            'description': result.description,
            'emoji': result.emoji
        })
    
    def _update_accuracy(self, profile, sign, confidence):
        """Update gesture accuracy statistics"""
        accuracy, created = GestureAccuracy.objects.get_or_create(
            user_profile=profile,
            gesture_sign=sign,
            defaults={'personalized_threshold': 0.8}
        )
        
        accuracy.attempts += 1
        if confidence >= accuracy.personalized_threshold:
            accuracy.successful += 1
        
        # Update average confidence
        total_confidence = accuracy.average_confidence * (accuracy.attempts - 1) + confidence
        accuracy.average_confidence = total_confidence / accuracy.attempts
        
        accuracy.save()


class GestureBatchView(APIView):
    """Handle batch gesture data uploads"""
    
    def post(self, request):
        """
        Store multiple gestures from a detection session.
        
        Expected input:
        {
            "session_id": "optional-session-id",
            "user_id": "required-user-id",
            "gestures": [
                {
                    "detected_sign": "A",
                    "confidence": 0.85,
                    "landmarks": [...],
                    ...
                }
            ],
            "user_profile": {
                "hand_size": "medium",
                "dominant_hand": "right"
            }
        }
        """
        serializer = GestureBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        gestures = serializer.validated_data['gestures']
        user_profile_data = serializer.validated_data.get('user_profile', {})
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            device_id=user_id,
            defaults={
                'hand_size': user_profile_data.get('hand_size', 'medium'),
                'dominant_hand': user_profile_data.get('dominant_hand', 'right')
            }
        )
        
        # Create session
        session = GestureSession.objects.create(
            user_profile=profile,
            session_context=gestures[0].get('session_context', 'batch_upload') if gestures else 'batch_upload'
        )
        
        stored_count = 0
        accuracy_updates = 0
        unique_signs = set()
        
        for gesture_data in gestures:
            try:
                detected_sign = gesture_data.get('detected_sign', gesture_data.get('detectedSign'))
                confidence = gesture_data.get('confidence', 0.0)
                
                if detected_sign:
                    unique_signs.add(detected_sign)
                    
                    GestureData.objects.create(
                        session=session,
                        user_profile=profile,
                        detected_sign=detected_sign,
                        confidence=confidence,
                        recognition_method=gesture_data.get('recognition_method', gesture_data.get('recognitionMethod', 'fingerpose')),
                        landmarks=gesture_data.get('landmarks'),
                        hand_shape=gesture_data.get('hand_shape', gesture_data.get('handShape')),
                        is_low_confidence=confidence < 0.7,
                        recognition_failed=gesture_data.get('recognition_failed', gesture_data.get('recognitionFailed', False))
                    )
                    stored_count += 1
                    
                    # Update accuracy
                    if confidence > 0:
                        accuracy, _ = GestureAccuracy.objects.get_or_create(
                            user_profile=profile,
                            gesture_sign=detected_sign
                        )
                        accuracy.attempts += 1
                        if confidence >= 0.8:
                            accuracy.successful += 1
                        total_conf = accuracy.average_confidence * (accuracy.attempts - 1) + confidence
                        accuracy.average_confidence = total_conf / accuracy.attempts
                        accuracy.save()
                        accuracy_updates += 1
                        
            except Exception as e:
                logger.error(f"Error storing gesture: {e}")
        
        # Update session stats
        session.gesture_count = stored_count
        if stored_count > 0:
            session.average_confidence = sum(
                g.get('confidence', 0) for g in gestures
            ) / len(gestures)
        session.save()
        
        # Update profile stats
        profile.total_gestures = GestureData.objects.filter(user_profile=profile).count()
        profile.session_count = GestureSession.objects.filter(user_profile=profile).count()
        profile.save()
        
        logger.info(f"📊 Stored {stored_count}/{len(gestures)} gestures from user {user_id[-6:]}")
        
        return Response({
            'success': True,
            'message': 'Gesture data stored successfully',
            'stored': stored_count,
            'accuracy_updates': accuracy_updates,
            'unique_signs': len(unique_signs),
            'session_id': str(session.id)
        })


class GestureStatsView(APIView):
    """Get user gesture statistics"""
    
    def get(self, request, user_id):
        """Get comprehensive stats for a user"""
        try:
            profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            try:
                profile = UserProfile.objects.get(device_id=user_id)
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': 'User profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get recent gestures
        recent_gestures = GestureData.objects.filter(
            user_profile=profile
        ).order_by('-timestamp')[:50]
        
        # Get accuracy data
        accuracy_data = GestureAccuracy.objects.filter(
            user_profile=profile
        ).order_by('-successful')[:10]
        
        # Calculate overall accuracy
        total_attempts = sum(a.attempts for a in accuracy_data)
        total_successful = sum(a.successful for a in accuracy_data)
        overall_accuracy = total_successful / total_attempts if total_attempts > 0 else 0
        
        return Response({
            'success': True,
            'stats': {
                'user_id': str(profile.id),
                'profile': {
                    'total_gestures': profile.total_gestures,
                    'average_accuracy': overall_accuracy,
                    'session_count': profile.session_count,
                    'hand_size': profile.hand_size,
                    'dominant_hand': profile.dominant_hand,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat()
                },
                'recent_activity': GestureDataSerializer(recent_gestures, many=True).data,
                'top_signs': GestureAccuracySerializer(accuracy_data, many=True).data,
                'total_unique_signs': GestureAccuracy.objects.filter(user_profile=profile).count()
            }
        })


class PersonalizedThresholdsView(APIView):
    """Get personalized detection thresholds for a user"""
    
    def get(self, request, user_id):
        """Get personalized thresholds based on user performance"""
        try:
            profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            try:
                profile = UserProfile.objects.get(device_id=user_id)
            except UserProfile.DoesNotExist:
                return Response({
                    'success': True,
                    'thresholds': {},
                    'message': 'No personalized data available, using default thresholds'
                })
        
        accuracy_data = GestureAccuracy.objects.filter(
            user_profile=profile,
            attempts__gte=5  # Need at least 5 attempts
        )
        
        thresholds = {}
        for acc in accuracy_data:
            accuracy = acc.successful / acc.attempts if acc.attempts > 0 else 0
            
            if accuracy > 0.9 and acc.average_confidence > 0.85:
                threshold = 0.9  # Higher threshold for confident signs
            elif accuracy < 0.5:
                threshold = 0.7  # Lower threshold for struggling signs
            else:
                threshold = 0.8  # Default threshold
            
            thresholds[acc.gesture_sign] = threshold
        
        return Response({
            'success': True,
            'thresholds': thresholds,
            'total_signs': accuracy_data.count(),
            'personalized_signs': len(thresholds)
        })


class ASLSignViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference data for ASL signs"""
    queryset = ASLSign.objects.all()
    serializer_class = ASLSignSerializer
    
    @action(detail=False, methods=['get'])
    def alphabet(self, request):
        """Get all ASL alphabet signs with descriptions"""
        alphabet = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            alphabet.append({
                'letter': letter,
                'description': ASL_DESCRIPTIONS.get(letter, ''),
                'emoji': HAND_SHAPES.get(letter, ''),
                'hand_shape': HAND_SHAPES.get(letter, '')
            })
        
        return Response({
            'alphabet': alphabet,
            'total': len(alphabet)
        })


class AnalyticsView(APIView):
    """Admin analytics for all gesture data"""
    
    def get(self, request):
        """Get system-wide analytics"""
        total_users = UserProfile.objects.count()
        total_sessions = GestureSession.objects.count()
        total_gestures = GestureData.objects.count()
        
        # Average confidence across all detections
        avg_confidence = GestureData.objects.aggregate(
            avg=Avg('confidence')
        )['avg'] or 0.0
        
        # Most detected signs
        top_signs = GestureData.objects.values('detected_sign').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence')
        ).order_by('-count')[:10]
        
        return Response({
            'success': True,
            'analytics': {
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_gestures': total_gestures,
                'average_confidence': round(avg_confidence, 3),
                'top_signs': list(top_signs),
                'database_info': {
                    'storage': 'SQLite Database',
                    'persistent': True
                }
            }
        })


class ImageDetectionView(APIView):
    """
    Detect signs from base64 encoded camera frames.
    This allows the Flutter app to send images for server-side processing.
    """
    
    def post(self, request):
        """
        Detect sign language from a camera frame image.
        
        Expected input:
        {
            "image": "base64-encoded-image-data",
            "user_id": "optional-user-id"
        }
        """
        image_data = request.data.get('image')
        user_id = request.data.get('user_id')
        
        if not image_data:
            return Response(
                {'error': 'image is required (base64 encoded)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to use MediaPipe for landmark detection
        try:
            from .mediapipe_detector import detect_landmarks_from_base64, is_available
            
            if not is_available():
                return Response({
                    'detected': False,
                    'error': 'Server-side detection not available',
                    'message': 'MediaPipe not installed. Send landmarks directly to /api/detect/'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
            
            # Detect landmarks from image
            landmarks = detect_landmarks_from_base64(image_data)
            
            if not landmarks:
                return Response({
                    'detected': False,
                    'message': 'No hand detected in image'
                })
            
            # Classify the detected landmarks
            result = detect_sign(landmarks)
            
            if not result:
                return Response({
                    'detected': False,
                    'message': 'Hand detected but gesture not recognized'
                })
            
            # Optionally save gesture data
            if user_id:
                try:
                    profile = UserProfile.objects.get(device_id=user_id)
                    GestureData.objects.create(
                        user_profile=profile,
                        detected_sign=result.sign,
                        confidence=result.confidence,
                        recognition_method='image_detection',
                        landmarks=landmarks,
                        hand_shape=result.hand_shape,
                        is_low_confidence=result.confidence < 0.7
                    )
                except UserProfile.DoesNotExist:
                    pass
            
            return Response({
                'detected': True,
                'sign': result.sign,
                'confidence': result.confidence,
                'hand_shape': result.hand_shape,
                'description': result.description,
                'emoji': result.emoji,
                'landmarks': landmarks  # Return landmarks for client-side visualization
            })
            
        except ImportError:
            return Response({
                'detected': False,
                'error': 'MediaPipe module not found',
                'message': 'Install with: pip install mediapipe opencv-python numpy'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)
        
        except Exception as e:
            logger.error(f"Image detection error: {e}")
            return Response({
                'detected': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
