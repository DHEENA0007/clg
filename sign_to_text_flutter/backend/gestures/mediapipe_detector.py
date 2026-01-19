"""
Hand Landmark Detection using MediaPipe Tasks API

This module provides hand landmark detection from images.
Requires: mediapipe, opencv-python, numpy

Install with:
pip install mediapipe opencv-python numpy

Uses the new MediaPipe Tasks API (v0.10.10+)
"""
import base64
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

# Try to import MediaPipe - optional dependency
try:
    import cv2
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
    logger.info("MediaPipe Tasks API is available for server-side hand detection")
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    logger.warning(f"MediaPipe not available. Server-side hand detection disabled. Error: {e}")
    logger.warning("Install with: pip install mediapipe opencv-python numpy")


# Path to the hand landmarker model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')

# Download URL for the model
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"


def download_model():
    """Download the hand landmarker model if not present"""
    if os.path.exists(MODEL_PATH):
        return True
    
    try:
        import urllib.request
        logger.info(f"Downloading hand landmarker model from {MODEL_URL}")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        logger.info("Model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False


class MediaPipeHandDetector:
    """
    Hand landmark detection using MediaPipe Tasks API.
    Detects 21 hand landmarks from an image.
    """
    
    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe is not installed")
        
        # Download model if needed
        if not download_model():
            raise RuntimeError("Failed to download hand landmarker model")
        
        # Create hand landmarker
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
    
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
            height, width = image.shape[:2]
            
            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            # Detect hand landmarks
            detection_result = self.detector.detect(mp_image)
            
            if not detection_result.hand_landmarks:
                return None
            
            # Get first hand
            hand_landmarks = detection_result.hand_landmarks[0]
            
            # Convert to list format
            landmarks = []
            for lm in hand_landmarks:
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
        if hasattr(self, 'detector'):
            self.detector.close()


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
