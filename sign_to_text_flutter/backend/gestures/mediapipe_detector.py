"""
Hand Landmark Detection using MediaPipe (Optional)

This module provides hand landmark detection from images.
Requires: mediapipe, opencv-python, numpy

Install with:
pip install mediapipe opencv-python numpy

If these packages are not available, the API will fall back to 
accepting pre-computed landmarks from the client.
"""
import base64
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import MediaPipe - optional dependency
try:
    import cv2
    import numpy as np
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    logger.info("MediaPipe is available for server-side hand detection")
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available. Server-side hand detection disabled.")
    logger.warning("Install with: pip install mediapipe opencv-python numpy")


class MediaPipeHandDetector:
    """
    Hand landmark detection using MediaPipe.
    Detects 21 hand landmarks from an image.
    """
    
    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe is not installed")
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    
    def detect_from_base64(self, base64_image: str) -> Optional[List[List[float]]]:
        """
        Detect hand landmarks from a base64 encoded image.
        
        Args:
            base64_image: Base64 encoded JPEG/PNG image
            
        Returns:
            List of 21 landmarks with [x, y, z] coordinates, or None if no hand detected
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image")
                return None
            
            return self.detect_from_image(image)
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            return None
    
    def detect_from_image(self, image) -> Optional[List[List[float]]]:
        """
        Detect hand landmarks from a numpy/cv2 image.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            List of 21 landmarks with [x, y, z] coordinates, or None if no hand detected
        """
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.hands.process(image_rgb)
            
            if not results.multi_hand_landmarks:
                return None
            
            # Get first hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Convert to list format
            height, width = image.shape[:2]
            landmarks = []
            
            for lm in hand_landmarks.landmark:
                # Convert normalized coordinates to pixel coordinates
                landmarks.append([
                    lm.x * width,
                    lm.y * height,
                    lm.z * width  # Z is relative to wrist depth
                ])
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Error detecting hand landmarks: {e}")
            return None
    
    def close(self):
        """Release MediaPipe resources"""
        self.hands.close()


# Global detector instance (lazy loaded)
_detector = None


def get_detector() -> Optional[MediaPipeHandDetector]:
    """Get or create the MediaPipe hand detector instance"""
    global _detector
    
    if not MEDIAPIPE_AVAILABLE:
        return None
    
    if _detector is None:
        try:
            _detector = MediaPipeHandDetector()
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe: {e}")
            return None
    
    return _detector


def detect_landmarks_from_base64(base64_image: str) -> Optional[List[List[float]]]:
    """
    Convenience function to detect landmarks from base64 image.
    
    Args:
        base64_image: Base64 encoded image (without data URL prefix)
        
    Returns:
        List of 21 landmarks or None
    """
    detector = get_detector()
    if detector is None:
        return None
    
    # Remove data URL prefix if present
    if base64_image.startswith('data:'):
        base64_image = base64_image.split(',', 1)[1]
    
    return detector.detect_from_base64(base64_image)


def is_available() -> bool:
    """Check if MediaPipe hand detection is available"""
    return MEDIAPIPE_AVAILABLE
