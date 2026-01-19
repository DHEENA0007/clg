"""
Sign Language Detection Service
Ported from the React/Node.js implementation to Python
"""
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Landmark:
    """Hand landmark point"""
    x: float
    y: float
    z: float = 0.0


@dataclass
class DetectionResult:
    """Result of sign detection"""
    sign: str
    confidence: float
    hand_shape: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None


# ASL Sign Definitions
ASL_DESCRIPTIONS = {
    'A': 'Thumb beside closed fist',
    'B': 'Four fingers straight up',
    'C': 'Curved hand shape',
    'D': 'Index up, circle with others',
    'E': 'Fingertips bent down',
    'F': 'Index-thumb circle, three up',
    'G': 'Point sideways',
    'H': 'Two fingers sideways',
    'I': 'Pinky extended',
    'J': 'Draw J shape',
    'K': 'Index up, middle out',
    'L': 'Thumb-index L shape',
    'M': 'Three fingers over thumb',
    'N': 'Two fingers over thumb',
    'O': 'Fingertips form circle',
    'P': 'K pointing down',
    'Q': 'G pointing down',
    'R': 'Cross index-middle fingers',
    'S': 'Closed fist',
    'T': 'Fist with thumb between',
    'U': 'Two fingers together up',
    'V': 'Two fingers apart (Peace)',
    'W': 'Three fingers up',
    'X': 'Index crooked',
    'Y': 'Thumb-pinky extended',
    'Z': 'Draw Z motion',
    '👍': 'Thumbs up',
    '👋': 'Open hand wave',
    '☝️': 'Pointing up',
}

HAND_SHAPES = {
    'A': '✊', 'B': '🖐️', 'C': '🤏', 'D': '☝️', 'E': '✊',
    'F': '👌', 'G': '👉', 'H': '👈', 'I': '🤙', 'J': '🤙',
    'K': '✌️', 'L': '🤟', 'M': '👊', 'N': '👊', 'O': '⭕',
    'P': '👇', 'Q': '👇', 'R': '🤞', 'S': '✊', 'T': '👊',
    'U': '🤘', 'V': '✌️', 'W': '🤟', 'X': '🤞', 'Y': '🤙', 'Z': '👉',
    '👍': '👍', '👋': '👋', '☝️': '☝️'
}


class SignDetector:
    """
    Sign Language Detection using hand landmarks.
    Implements the same logic as the JavaScript fingerpose library.
    """
    
    # Finger indices in MediaPipe hand model
    FINGER_TIPS = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
    FINGER_BASES = [2, 5, 9, 13, 17]
    FINGER_MIDS = [3, 6, 10, 14, 18]
    FINGER_PIPS = [3, 6, 10, 14, 18]  # PIP joints
    
    def __init__(self):
        self.confidence_threshold = 0.65
        self.gesture_patterns = self._init_gesture_patterns()
    
    def _init_gesture_patterns(self) -> Dict:
        """Initialize gesture patterns based on fingerpose definitions"""
        patterns = {
            'A': {'curl': [0.5, 1.0, 1.0, 1.0, 1.0], 'extended': [True, False, False, False, False]},
            'B': {'curl': [0.5, 0.0, 0.0, 0.0, 0.0], 'extended': [False, True, True, True, True]},
            'C': {'curl': [0.5, 0.5, 0.5, 0.5, 0.5], 'all_half': True},
            'D': {'curl': [0.5, 0.0, 1.0, 1.0, 1.0], 'extended': [False, True, False, False, False]},
            'E': {'curl': [1.0, 1.0, 1.0, 1.0, 1.0], 'all_curled': True},
            'F': {'curl': [0.5, 0.5, 0.0, 0.0, 0.0], 'extended': [False, False, True, True, True]},
            'I': {'curl': [0.5, 1.0, 1.0, 1.0, 0.0], 'extended': [False, False, False, False, True]},
            'L': {'curl': [0.0, 0.0, 1.0, 1.0, 1.0], 'extended': [True, True, False, False, False]},
            'V': {'curl': [0.5, 0.0, 0.0, 1.0, 1.0], 'extended': [False, True, True, False, False]},
            'W': {'curl': [0.5, 0.0, 0.0, 0.0, 1.0], 'extended': [False, True, True, True, False]},
            'Y': {'curl': [0.0, 1.0, 1.0, 1.0, 0.0], 'extended': [True, False, False, False, True]},
            '👍': {'curl': [0.0, 1.0, 1.0, 1.0, 1.0], 'extended': [True, False, False, False, False], 'thumb_up': True},
            '👋': {'curl': [0.0, 0.0, 0.0, 0.0, 0.0], 'extended': [True, True, True, True, True]},
        }
        return patterns
    
    def detect(self, landmarks: List[List[float]]) -> Optional[DetectionResult]:
        """
        Detect sign language gesture from hand landmarks.
        
        Args:
            landmarks: List of 21 landmarks, each with [x, y, z] coordinates
            
        Returns:
            DetectionResult or None if no confident detection
        """
        if not landmarks or len(landmarks) != 21:
            logger.debug("Invalid landmarks: expected 21 points")
            return None
        
        try:
            # Convert to Landmark objects
            points = [Landmark(x=l[0], y=l[1], z=l[2] if len(l) > 2 else 0.0) for l in landmarks]
            
            # Calculate finger states
            extended = self._calculate_finger_extensions(points)
            curls = self._calculate_finger_curls(points)
            
            # Match against patterns
            best_match, confidence = self._match_gesture(extended, curls, points)
            
            if best_match and confidence >= self.confidence_threshold:
                return DetectionResult(
                    sign=best_match,
                    confidence=confidence,
                    hand_shape=HAND_SHAPES.get(best_match),
                    description=ASL_DESCRIPTIONS.get(best_match),
                    emoji=HAND_SHAPES.get(best_match)
                )
            
            # Fallback to basic detection
            return self._basic_detection(extended, points)
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return None
    
    def _calculate_finger_extensions(self, landmarks: List[Landmark]) -> List[bool]:
        """Calculate which fingers are extended"""
        extended = []
        
        # Thumb (horizontal check)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_extended = abs(thumb_tip.x - thumb_ip.x) > 30
        extended.append(thumb_extended)
        
        # Other fingers (vertical check)
        for i in range(1, 5):
            tip_idx = self.FINGER_TIPS[i]
            pip_idx = self.FINGER_PIPS[i]
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            # Finger is extended if tip is above PIP joint
            is_extended = tip.y < pip.y - 20
            extended.append(is_extended)
        
        return extended
    
    def _calculate_finger_curls(self, landmarks: List[Landmark]) -> List[float]:
        """Calculate curl amount for each finger (0.0 = straight, 1.0 = fully curled)"""
        curls = []
        
        for i in range(5):
            tip_idx = self.FINGER_TIPS[i]
            base_idx = self.FINGER_BASES[i]
            mid_idx = self.FINGER_MIDS[i]
            
            tip = landmarks[tip_idx]
            base = landmarks[base_idx]
            mid = landmarks[mid_idx]
            
            # Distance from base to tip
            base_tip_dist = self._distance(tip, base)
            # Distance from base to mid
            base_mid_dist = self._distance(mid, base)
            
            # Calculate curl ratio
            if base_mid_dist > 0:
                if base_tip_dist < base_mid_dist * 1.2:
                    curl = 1.0  # Fully curled
                elif base_tip_dist > base_mid_dist * 2.0:
                    curl = 0.0  # Straight
                else:
                    curl = 0.5  # Half curled
            else:
                curl = 0.5
            
            curls.append(curl)
        
        return curls
    
    def _match_gesture(self, extended: List[bool], curls: List[float], landmarks: List[Landmark]) -> Tuple[Optional[str], float]:
        """Match current hand state against gesture patterns"""
        best_match = None
        best_score = 0.0
        
        for sign, pattern in self.gesture_patterns.items():
            score = self._calculate_pattern_score(extended, curls, pattern, landmarks)
            if score > best_score:
                best_score = score
                best_match = sign
        
        return best_match, best_score
    
    def _calculate_pattern_score(self, extended: List[bool], curls: List[float], pattern: Dict, landmarks: List[Landmark]) -> float:
        """Calculate how well the current hand matches a pattern"""
        score = 0.0
        total_checks = 0
        
        if 'extended' in pattern:
            expected_extended = pattern['extended']
            for i, (actual, expected) in enumerate(zip(extended, expected_extended)):
                total_checks += 1
                if actual == expected:
                    score += 1.0
        
        if 'all_curled' in pattern and pattern['all_curled']:
            curl_score = sum(1.0 for c in curls if c > 0.7) / 5.0
            score += curl_score * 5
            total_checks += 5
        
        if 'all_half' in pattern and pattern['all_half']:
            half_score = sum(1.0 for c in curls if 0.3 <= c <= 0.7) / 5.0
            score += half_score * 5
            total_checks += 5
        
        if 'thumb_up' in pattern and pattern['thumb_up']:
            thumb_tip = landmarks[4]
            wrist = landmarks[0]
            if thumb_tip.y < wrist.y - 50:  # Thumb pointing up
                score += 2.0
            total_checks += 2
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _basic_detection(self, extended: List[bool], landmarks: List[Landmark]) -> Optional[DetectionResult]:
        """Fallback basic detection based on finger count"""
        extended_count = sum(1 for e in extended if e)
        wrist = landmarks[0]
        
        # Calculate average distance from wrist to fingertips
        avg_distance = sum(
            self._distance(landmarks[i], wrist) 
            for i in self.FINGER_TIPS[1:]
        ) / 4
        
        # Detection logic
        sign = None
        confidence = 0.6
        
        if extended_count == 0 and avg_distance < 150:
            sign = 'A'
            confidence = 0.75
        elif extended_count == 2 and extended[1] and extended[2]:
            sign = 'V'
            confidence = 0.78
        elif extended_count == 1 and extended[1]:
            sign = 'D'
            confidence = 0.72
        elif extended_count == 1 and extended[0]:
            sign = '👍'
            confidence = 0.70
        elif extended_count == 5:
            sign = '👋'
            confidence = 0.75
        elif extended_count == 3 and extended[1] and extended[2] and extended[3]:
            sign = 'W'
            confidence = 0.70
        elif extended_count == 4 and not extended[0]:
            sign = 'B'
            confidence = 0.68
        elif extended_count == 2 and extended[0] and extended[1]:
            sign = 'L'
            confidence = 0.67
        
        if sign:
            return DetectionResult(
                sign=sign,
                confidence=confidence,
                hand_shape=HAND_SHAPES.get(sign),
                description=ASL_DESCRIPTIONS.get(sign),
                emoji=HAND_SHAPES.get(sign)
            )
        
        return DetectionResult(
            sign=f'{extended_count} fingers',
            confidence=0.50,
            hand_shape=None,
            description=None,
            emoji=None
        )
    
    @staticmethod
    def _distance(p1: Landmark, p2: Landmark) -> float:
        """Calculate Euclidean distance between two landmarks"""
        return math.sqrt(
            (p2.x - p1.x) ** 2 + 
            (p2.y - p1.y) ** 2 + 
            (p2.z - p1.z) ** 2
        )


# Global detector instance
sign_detector = SignDetector()


def detect_sign(landmarks: List[List[float]]) -> Optional[DetectionResult]:
    """
    Public API to detect sign from landmarks.
    
    Args:
        landmarks: 21 hand landmarks with [x, y, z] coordinates
        
    Returns:
        DetectionResult or None
    """
    return sign_detector.detect(landmarks)
