"""
Advanced ASL Sign Language Detection Service
Comprehensive detection for ASL Alphabet (A-Z) and Numbers (0-9)
Using detailed 21-point hand landmark analysis from MediaPipe
"""
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FingerState(Enum):
    """Finger curl states"""
    EXTENDED = 0      # Finger fully straight
    HALF_CURLED = 1   # Finger partially bent
    CURLED = 2        # Finger fully bent/closed


class ThumbPosition(Enum):
    """Thumb position relative to hand"""
    ACROSS_PALM = 0   # Thumb tucked across palm
    BESIDE_FIST = 1   # Thumb beside closed fist
    EXTENDED_OUT = 2  # Thumb extended outward
    EXTENDED_UP = 3   # Thumb pointing up
    TOUCHING_FINGER = 4  # Thumb touching another finger


@dataclass
class Landmark:
    """Hand landmark point with normalized coordinates"""
    x: float
    y: float
    z: float = 0.0


@dataclass
class FingerAnalysis:
    """Complete analysis of a single finger"""
    is_extended: bool
    curl_state: FingerState
    curl_ratio: float  # 0.0 = straight, 1.0 = fully curled
    tip_to_wrist_distance: float
    direction_angle: float  # Angle of finger direction


@dataclass
class HandAnalysis:
    """Complete analysis of hand pose"""
    fingers: List[FingerAnalysis]  # [thumb, index, middle, ring, pinky]
    thumb_position: ThumbPosition
    palm_direction: str  # 'up', 'down', 'forward', 'backward'
    hand_rotation: float
    finger_spread: float  # How spread apart the fingers are
    fingers_touching: Dict[str, bool]  # e.g., {'thumb_index': True}


@dataclass
class DetectionResult:
    """Result of sign detection"""
    sign: str
    confidence: float
    category: str  # 'letter', 'number', 'gesture'
    hand_shape: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None


# Complete ASL definitions
ASL_ALPHABET_DESCRIPTIONS = {
    'A': 'Closed fist with thumb alongside, not tucked',
    'B': 'Flat hand, fingers together pointing up, thumb tucked across palm',
    'C': 'Curved hand forming a C shape, thumb and fingers opposed',
    'D': 'Index finger up, thumb touches middle of curled middle finger',
    'E': 'Fingertips bent down touching thumb, all bunched together',
    'F': 'Thumb and index make circle (OK sign), other 3 fingers extended up',
    'G': 'Index finger and thumb extended parallel, pointing sideways',
    'H': 'Index and middle fingers extended together horizontally',
    'I': 'Fist with pinky finger extended upward',
    'J': 'Same as I but draw a J motion with pinky',
    'K': 'Index finger up, middle finger forward at angle, thumb between them',
    'L': 'Index finger up, thumb out at 90 degrees forming L shape',
    'M': 'Fist with thumb under curled index, middle, and ring fingers',
    'N': 'Fist with thumb under curled index and middle fingers',
    'O': 'All fingertips and thumb touch to form a circle',
    'P': 'Like K but pointed downward',
    'Q': 'Thumb and index extended downward, like G pointing down',
    'R': 'Index and middle fingers crossed',
    'S': 'Fist with thumb across curled fingers',
    'T': 'Fist with thumb tucked between index and middle fingers',
    'U': 'Index and middle fingers extended together pointing up',
    'V': 'Index and middle fingers extended apart (peace/victory sign)',
    'W': 'Index, middle, and ring fingers extended apart',
    'X': 'Index finger crooked/hooked',
    'Y': 'Thumb and pinky extended, other fingers curled (hang loose)',
    'Z': 'Index finger draws Z shape in air',
}

# Backward compatibility alias
ASL_DESCRIPTIONS = ASL_ALPHABET_DESCRIPTIONS

ASL_NUMBER_DESCRIPTIONS = {
    '0': 'All fingers form circle with thumb (like O)',
    '1': 'Index finger only extended upward',
    '2': 'Index and middle fingers extended apart (like V)',
    '3': 'Thumb, index, and middle fingers extended',
    '4': 'All four fingers extended, thumb curled across palm',
    '5': 'All five fingers and thumb extended (open palm)',
    '6': 'Thumb and pinky extended, touching other 3 fingers with thumb',
    '7': 'Thumb and ring finger touch, index, middle, pinky extended',
    '8': 'Thumb and middle finger touch, index, ring, pinky extended',
    '9': 'Thumb and index finger touch circled, other 3 extended',
    '10': 'Thumb up, hand shakes (thumbs up motion)',
}

# Emoji representations
HAND_SHAPES = {
    'A': '✊', 'B': '🖐️', 'C': '🤏', 'D': '☝️', 'E': '✊',
    'F': '👌', 'G': '👉', 'H': '🤞', 'I': '🤙', 'J': '🤙',
    'K': '✌️', 'L': '🤟', 'M': '✊', 'N': '✊', 'O': '👌',
    'P': '👇', 'Q': '👇', 'R': '🤞', 'S': '✊', 'T': '✊',
    'U': '🤘', 'V': '✌️', 'W': '🤟', 'X': '☝️', 'Y': '🤙', 'Z': '👆',
    '0': '👌', '1': '☝️', '2': '✌️', '3': '🤟', '4': '🖐️',
    '5': '🖐️', '6': '🤙', '7': '🤟', '8': '🤟', '9': '👌', '10': '👍',
    'THUMBS_UP': '👍', 'WAVE': '👋', 'POINT': '☝️', 'OK': '👌',
    'PEACE': '✌️', 'ROCK': '🤘', 'CALL': '🤙', 'LOVE': '🤟',
}


class AdvancedSignDetector:
    """
    Advanced ASL Sign Language Detection using detailed hand landmark analysis.
    Implements precise finger state detection for all ASL letters (A-Z) and numbers (0-9).
    """
    
    # MediaPipe hand landmark indices
    WRIST = 0
    THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
    INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
    RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
    PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20
    
    # Finger landmark groups
    FINGER_LANDMARKS = {
        'thumb': [1, 2, 3, 4],     # CMC, MCP, IP, TIP
        'index': [5, 6, 7, 8],     # MCP, PIP, DIP, TIP
        'middle': [9, 10, 11, 12], # MCP, PIP, DIP, TIP
        'ring': [13, 14, 15, 16],  # MCP, PIP, DIP, TIP
        'pinky': [17, 18, 19, 20], # MCP, PIP, DIP, TIP
    }
    
    FINGER_TIPS = [4, 8, 12, 16, 20]
    FINGER_PIPS = [3, 6, 10, 14, 18]  # Second joint (IP for thumb, PIP for others)
    FINGER_MCPS = [2, 5, 9, 13, 17]   # Knuckles
    
    def __init__(self, confidence_threshold: float = 0.60):
        self.confidence_threshold = confidence_threshold
    
    def detect(self, landmarks: List[List[float]]) -> Optional[DetectionResult]:
        """
        Detect ASL sign from 21 hand landmarks.
        
        Args:
            landmarks: List of 21 [x, y, z] coordinates from MediaPipe
            
        Returns:
            DetectionResult with sign, confidence, and metadata
        """
        if not landmarks or len(landmarks) != 21:
            logger.debug(f"Invalid landmarks: expected 21, got {len(landmarks) if landmarks else 0}")
            return None
        
        try:
            # Convert to Landmark objects
            points = [Landmark(x=lm[0], y=lm[1], z=lm[2] if len(lm) > 2 else 0.0) for lm in landmarks]
            
            # Perform detailed hand analysis
            analysis = self._analyze_hand(points)
            
            # Try to match against all known signs
            result = self._match_sign(analysis, points)
            
            return result
            
        except Exception as e:
            logger.error(f"Detection error: {e}", exc_info=True)
            return None
    
    def _analyze_hand(self, landmarks: List[Landmark]) -> HandAnalysis:
        """Perform comprehensive hand analysis"""
        fingers = []
        wrist = landmarks[self.WRIST]
        
        # Analyze each finger
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        for i, name in enumerate(finger_names):
            finger_analysis = self._analyze_finger(landmarks, i, wrist)
            fingers.append(finger_analysis)
        
        # Analyze thumb position
        thumb_position = self._analyze_thumb_position(landmarks)
        
        # Calculate palm direction
        palm_direction = self._calculate_palm_direction(landmarks)
        
        # Calculate hand rotation
        hand_rotation = self._calculate_hand_rotation(landmarks)
        
        # Calculate finger spread
        finger_spread = self._calculate_finger_spread(landmarks)
        
        # Check which fingers are touching
        fingers_touching = self._check_fingers_touching(landmarks)
        
        return HandAnalysis(
            fingers=fingers,
            thumb_position=thumb_position,
            palm_direction=palm_direction,
            hand_rotation=hand_rotation,
            finger_spread=finger_spread,
            fingers_touching=fingers_touching
        )
    
    def _analyze_finger(self, landmarks: List[Landmark], finger_idx: int, wrist: Landmark) -> FingerAnalysis:
        """Analyze a single finger's state"""
        tip_idx = self.FINGER_TIPS[finger_idx]
        pip_idx = self.FINGER_PIPS[finger_idx]
        mcp_idx = self.FINGER_MCPS[finger_idx]
        
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        mcp = landmarks[mcp_idx]
        
        # Calculate extension (different logic for thumb vs other fingers)
        if finger_idx == 0:  # Thumb
            is_extended = self._is_thumb_extended(landmarks)
        else:
            is_extended = self._is_finger_extended(tip, pip, mcp)
        
        # Calculate curl ratio
        curl_ratio = self._calculate_curl_ratio(landmarks, finger_idx)
        
        # Determine curl state
        if curl_ratio < 0.3:
            curl_state = FingerState.EXTENDED
        elif curl_ratio < 0.6:
            curl_state = FingerState.HALF_CURLED
        else:
            curl_state = FingerState.CURLED
        
        # Calculate tip to wrist distance
        tip_to_wrist = self._distance(tip, wrist)
        
        # Calculate finger direction angle
        direction_angle = math.atan2(tip.y - mcp.y, tip.x - mcp.x)
        
        return FingerAnalysis(
            is_extended=is_extended,
            curl_state=curl_state,
            curl_ratio=curl_ratio,
            tip_to_wrist_distance=tip_to_wrist,
            direction_angle=direction_angle
        )
    
    def _is_thumb_extended(self, landmarks: List[Landmark]) -> bool:
        """Check if thumb is extended (uses different logic than other fingers)"""
        thumb_tip = landmarks[self.THUMB_TIP]
        thumb_ip = landmarks[self.THUMB_IP]
        thumb_mcp = landmarks[self.THUMB_MCP]
        index_mcp = landmarks[self.INDEX_MCP]
        
        # Check horizontal distance from thumb tip to index base
        horizontal_extension = abs(thumb_tip.x - index_mcp.x)
        
        # Check if thumb is extended outward
        thumb_length = self._distance(thumb_tip, thumb_mcp)
        
        return horizontal_extension > thumb_length * 0.5
    
    def _is_finger_extended(self, tip: Landmark, pip: Landmark, mcp: Landmark) -> bool:
        """Check if a finger (non-thumb) is extended"""
        # Finger is extended if tip is higher than PIP (considering y increases downward)
        # and the finger is relatively straight
        
        # Primary check: tip above PIP
        tip_above_pip = tip.y < pip.y
        
        # Secondary check: PIP above MCP (finger not bent backward)
        pip_above_mcp = pip.y < mcp.y
        
        # Calculate angle to check straightness
        tip_pip_dist = self._distance(tip, pip)
        pip_mcp_dist = self._distance(pip, mcp)
        tip_mcp_dist = self._distance(tip, mcp)
        
        # If finger is bent, tip-mcp distance will be much less than tip-pip + pip-mcp
        straightness = tip_mcp_dist / (tip_pip_dist + pip_mcp_dist + 0.001)
        
        return tip_above_pip and straightness > 0.85
    
    def _calculate_curl_ratio(self, landmarks: List[Landmark], finger_idx: int) -> float:
        """Calculate how curled a finger is (0.0 = straight, 1.0 = fully curled)"""
        tip_idx = self.FINGER_TIPS[finger_idx]
        mcp_idx = self.FINGER_MCPS[finger_idx]
        
        tip = landmarks[tip_idx]
        mcp = landmarks[mcp_idx]
        wrist = landmarks[self.WRIST]
        
        if finger_idx == 0:  # Thumb
            pip_idx = self.THUMB_IP
        else:
            pip_idx = self.FINGER_PIPS[finger_idx]
        
        pip = landmarks[pip_idx]
        
        # Calculate distances
        tip_to_mcp = self._distance(tip, mcp)
        pip_to_mcp = self._distance(pip, mcp)
        
        # For non-thumb fingers, also consider vertical position
        if finger_idx != 0:
            # If tip is below PIP (curled), increase curl ratio
            if tip.y > pip.y:
                vertical_curl = (tip.y - pip.y) / (pip_to_mcp + 0.001)
                return min(1.0, 0.5 + vertical_curl * 0.5)
            else:
                # Tip is above PIP (extended)
                extension = (pip.y - tip.y) / (pip_to_mcp + 0.001)
                return max(0.0, 0.5 - extension * 0.5)
        
        # For thumb, use distance-based calculation
        ratio = tip_to_mcp / (pip_to_mcp * 2 + 0.001)
        return max(0.0, min(1.0, 1.0 - ratio))
    
    def _analyze_thumb_position(self, landmarks: List[Landmark]) -> ThumbPosition:
        """Determine the thumb's position relative to the hand"""
        thumb_tip = landmarks[self.THUMB_TIP]
        thumb_ip = landmarks[self.THUMB_IP]
        index_mcp = landmarks[self.INDEX_MCP]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        wrist = landmarks[self.WRIST]
        
        # Check if thumb is pointing up
        if thumb_tip.y < thumb_ip.y and thumb_tip.y < index_mcp.y:
            return ThumbPosition.EXTENDED_UP
        
        # Check if thumb is extended outward
        thumb_index_dist = abs(thumb_tip.x - index_mcp.x)
        if thumb_index_dist > self._distance(thumb_tip, thumb_ip) * 1.5:
            return ThumbPosition.EXTENDED_OUT
        
        # Check if thumb is across palm (touching other fingers area)
        if abs(thumb_tip.x - middle_mcp.x) < 30:
            return ThumbPosition.ACROSS_PALM
        
        # Check if thumb is touching another finger
        for tip_idx in self.FINGER_TIPS[1:]:
            if self._distance(thumb_tip, landmarks[tip_idx]) < 30:
                return ThumbPosition.TOUCHING_FINGER
        
        return ThumbPosition.BESIDE_FIST
    
    def _calculate_palm_direction(self, landmarks: List[Landmark]) -> str:
        """Determine which way the palm is facing"""
        wrist = landmarks[self.WRIST]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        
        # Use z-coordinate difference to determine palm direction
        z_diff = middle_mcp.z - wrist.z
        
        if z_diff > 20:
            return 'backward'  # Palm facing away from camera
        elif z_diff < -20:
            return 'forward'   # Palm facing toward camera
        
        # Use y-coordinate for up/down
        y_diff = middle_mcp.y - wrist.y
        if y_diff < -30:
            return 'up'
        elif y_diff > 30:
            return 'down'
        
        return 'forward'
    
    def _calculate_hand_rotation(self, landmarks: List[Landmark]) -> float:
        """Calculate the rotation angle of the hand"""
        wrist = landmarks[self.WRIST]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        
        return math.atan2(middle_mcp.y - wrist.y, middle_mcp.x - wrist.x)
    
    def _calculate_finger_spread(self, landmarks: List[Landmark]) -> float:
        """Calculate how spread apart the fingers are"""
        index_tip = landmarks[self.INDEX_TIP]
        pinky_tip = landmarks[self.PINKY_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        pinky_mcp = landmarks[self.PINKY_MCP]
        
        tip_spread = self._distance(index_tip, pinky_tip)
        mcp_spread = self._distance(index_mcp, pinky_mcp)
        
        # Return ratio of tip spread to base spread
        return tip_spread / (mcp_spread + 0.001)
    
    def _check_fingers_touching(self, landmarks: List[Landmark]) -> Dict[str, bool]:
        """Check which finger tips are touching each other"""
        touching = {}
        threshold = 25  # Distance threshold for "touching"
        
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for i, name1 in enumerate(finger_names):
            for j, name2 in enumerate(finger_names[i+1:], i+1):
                tip1 = landmarks[self.FINGER_TIPS[i]]
                tip2 = landmarks[self.FINGER_TIPS[j]]
                dist = self._distance(tip1, tip2)
                touching[f'{name1}_{name2}'] = dist < threshold
        
        return touching
    
    def _match_sign(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> DetectionResult:
        """Match hand analysis to known ASL signs"""
        matches = []
        
        # Check all letters
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            confidence = self._check_letter(letter, analysis, landmarks)
            if confidence > 0.3:
                matches.append((letter, confidence, 'letter'))
        
        # Check all numbers
        for number in '0123456789':
            confidence = self._check_number(number, analysis, landmarks)
            if confidence > 0.3:
                matches.append((number, confidence, 'number'))
        
        # Check common gestures
        gesture_checks = [
            ('THUMBS_UP', self._check_thumbs_up(analysis, landmarks)),
            ('WAVE', self._check_wave(analysis, landmarks)),
            ('OK', self._check_ok(analysis, landmarks)),
            ('PEACE', self._check_peace(analysis, landmarks)),
            ('ROCK', self._check_rock(analysis, landmarks)),
            ('CALL', self._check_call(analysis, landmarks)),
            ('LOVE', self._check_love(analysis, landmarks)),
        ]
        
        for gesture, confidence in gesture_checks:
            if confidence > 0.3:
                matches.append((gesture, confidence, 'gesture'))
        
        # Sort by confidence and return best match
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if matches and matches[0][1] >= self.confidence_threshold:
            sign, confidence, category = matches[0]
            desc = ASL_ALPHABET_DESCRIPTIONS.get(sign) or ASL_NUMBER_DESCRIPTIONS.get(sign) or f"{sign} gesture"
            return DetectionResult(
                sign=sign,
                confidence=confidence,
                category=category,
                hand_shape=HAND_SHAPES.get(sign),
                description=desc,
                emoji=HAND_SHAPES.get(sign)
            )
        
        # Fallback: count extended fingers
        extended_count = sum(1 for f in analysis.fingers if f.is_extended)
        return DetectionResult(
            sign=f'{extended_count}',
            confidence=0.45,
            category='count',
            hand_shape=None,
            description=f'{extended_count} fingers detected',
            emoji=None
        )
    
    # ============== LETTER DETECTION METHODS ==============
    
    def _check_letter(self, letter: str, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Check if hand matches a specific letter"""
        method_name = f'_check_{letter.lower()}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(analysis, landmarks)
        return 0.0
    
    def _check_a(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """A: Closed fist with thumb beside (not tucked)"""
        score = 0.0
        
        # All fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:]):
            score += 0.4
        
        # Thumb beside fist, not extended
        if analysis.thumb_position == ThumbPosition.BESIDE_FIST:
            score += 0.3
        elif not analysis.fingers[0].is_extended:
            score += 0.2
        
        # Check thumb is not across palm
        thumb_tip = landmarks[self.THUMB_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        if thumb_tip.x < index_mcp.x - 10:  # Left of index (for right hand)
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_b(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """B: Flat hand, 4 fingers up, thumb across palm"""
        score = 0.0
        
        # Four fingers extended
        if all(f.is_extended for f in analysis.fingers[1:]):
            score += 0.4
        
        # Thumb curled/across palm
        if not analysis.fingers[0].is_extended:
            score += 0.2
        if analysis.thumb_position == ThumbPosition.ACROSS_PALM:
            score += 0.2
        
        # Fingers together (low spread)
        if analysis.finger_spread < 1.5:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_c(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """C: Curved hand forming C shape"""
        score = 0.0
        
        # All fingers half curled
        half_curled = sum(1 for f in analysis.fingers if f.curl_state == FingerState.HALF_CURLED)
        score += half_curled * 0.15
        
        # Thumb and fingers form arc
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        pinky_tip = landmarks[self.PINKY_TIP]
        
        # Gap between thumb and index
        gap = self._distance(thumb_tip, index_tip)
        if 40 < gap < 150:
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_d(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """D: Index up, others curled, thumb touches middle finger"""
        score = 0.0
        
        # Index extended
        if analysis.fingers[1].is_extended:
            score += 0.35
        
        # Middle, ring, pinky curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.3
        
        # Thumb touches middle finger
        if analysis.fingers_touching.get('thumb_middle', False):
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_e(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """E: All fingertips bent down, bunched together"""
        score = 0.0
        
        # All fingers curled or half-curled
        curled_count = sum(1 for f in analysis.fingers if f.curl_state != FingerState.EXTENDED)
        score += curled_count * 0.12
        
        # Fingertips close together (bunched)
        index_tip = landmarks[self.INDEX_TIP]
        pinky_tip = landmarks[self.PINKY_TIP]
        if self._distance(index_tip, pinky_tip) < 60:
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_f(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """F: Thumb-index circle (OK), middle/ring/pinky extended"""
        score = 0.0
        
        # Middle, ring, pinky extended
        if all(f.is_extended for f in analysis.fingers[2:]):
            score += 0.35
        
        # Thumb and index touching
        if analysis.fingers_touching.get('thumb_index', False):
            score += 0.35
        
        # Index not straight (curled to meet thumb)
        if not analysis.fingers[1].is_extended:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_g(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """G: Index and thumb pointing sideways"""
        score = 0.0
        
        # Index extended
        if analysis.fingers[1].is_extended:
            score += 0.25
        
        # Thumb extended
        if analysis.fingers[0].is_extended:
            score += 0.25
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.25
        
        # Hand pointed sideways (horizontal index)
        index_tip = landmarks[self.INDEX_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        if abs(index_tip.y - index_mcp.y) < 40:  # Horizontal
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_h(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """H: Index and middle fingers horizontal"""
        score = 0.0
        
        # Index and middle extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended:
            score += 0.35
        
        # Ring and pinky curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.25
        
        # Fingers horizontal
        index_tip = landmarks[self.INDEX_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        if abs(index_tip.y - index_mcp.y) < 50:
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_i(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """I: Only pinky extended"""
        score = 0.0
        
        # Pinky extended
        if analysis.fingers[4].is_extended:
            score += 0.45
        
        # All other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[:4]):
            score += 0.45
        
        return min(score, 1.0)
    
    def _check_j(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """J: Same as I but with motion (static detection same as I)"""
        return self._check_i(analysis, landmarks) * 0.9  # Slightly lower since it's motion-based
    
    def _check_k(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """K: Index up, middle at angle, thumb between"""
        score = 0.0
        
        # Index extended
        if analysis.fingers[1].is_extended:
            score += 0.25
        
        # Middle extended or half
        if analysis.fingers[2].curl_state != FingerState.CURLED:
            score += 0.2
        
        # Ring and pinky curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.25
        
        # Thumb between index and middle
        thumb_tip = landmarks[self.THUMB_TIP]
        index_pip = landmarks[self.INDEX_PIP]
        middle_pip = landmarks[self.MIDDLE_PIP]
        if index_pip.x < thumb_tip.x < middle_pip.x or middle_pip.x < thumb_tip.x < index_pip.x:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_l(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """L: Index up and thumb out at 90 degrees"""
        score = 0.0
        
        # Index extended
        if analysis.fingers[1].is_extended:
            score += 0.3
        
        # Thumb extended
        if analysis.fingers[0].is_extended:
            score += 0.3
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.25
        
        # Check L shape (90 degree angle)
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        wrist = landmarks[self.WRIST]
        
        # Thumb and index should be roughly perpendicular
        thumb_angle = math.atan2(thumb_tip.y - wrist.y, thumb_tip.x - wrist.x)
        index_angle = math.atan2(index_tip.y - wrist.y, index_tip.x - wrist.x)
        angle_diff = abs(thumb_angle - index_angle)
        if 0.8 < angle_diff < 2.3:  # Roughly 45-130 degrees apart
            score += 0.15
        
        return min(score, 1.0)
    
    def _check_m(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """M: Three fingers over thumb"""
        score = 0.0
        
        # Index, middle, ring curled over thumb
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:4]):
            score += 0.4
        
        # Pinky curled
        if analysis.fingers[4].curl_state == FingerState.CURLED:
            score += 0.2
        
        # Thumb under fingers
        thumb_tip = landmarks[self.THUMB_TIP]
        middle_pip = landmarks[self.MIDDLE_PIP]
        if thumb_tip.y > middle_pip.y:  # Thumb below middle finger
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_n(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """N: Two fingers over thumb"""
        score = 0.0
        
        # Index and middle curled over thumb
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:3]):
            score += 0.35
        
        # Ring and pinky also curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.25
        
        # Thumb under first two fingers
        thumb_tip = landmarks[self.THUMB_TIP]
        middle_pip = landmarks[self.MIDDLE_PIP]
        if thumb_tip.y > middle_pip.y:
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_o(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """O: All fingertips and thumb touch forming circle"""
        score = 0.0
        
        # All fingers curved
        curved_count = sum(1 for f in analysis.fingers 
                         if f.curl_state in [FingerState.HALF_CURLED, FingerState.CURLED])
        score += curved_count * 0.1
        
        # Fingertips close together
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        
        if self._distance(thumb_tip, index_tip) < 40:
            score += 0.4
        
        return min(score, 1.0)
    
    def _check_p(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """P: Like K but pointing down"""
        # Similar to K but hand is rotated
        k_score = self._check_k(analysis, landmarks)
        
        # Check downward orientation
        index_tip = landmarks[self.INDEX_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        if index_tip.y > index_mcp.y:  # Pointing down
            return k_score * 0.95
        
        return k_score * 0.3
    
    def _check_q(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Q: Like G but pointing down"""
        g_score = self._check_g(analysis, landmarks)
        
        # Check downward orientation
        index_tip = landmarks[self.INDEX_TIP]
        index_mcp = landmarks[self.INDEX_MCP]
        if index_tip.y > index_mcp.y:  # Pointing down
            return g_score * 0.95
        
        return g_score * 0.3
    
    def _check_r(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """R: Index and middle crossed"""
        score = 0.0
        
        # Index and middle extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended:
            score += 0.3
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.2
        
        # Check if fingers are crossed (index and middle tips close)
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        index_dip = landmarks[self.INDEX_DIP]
        middle_dip = landmarks[self.MIDDLE_DIP]
        
        # Tips should be close and crossed
        if self._distance(index_tip, middle_tip) < 30:
            score += 0.25
        
        # Check crossing at DIP level
        if abs(index_dip.x - middle_dip.x) > abs(index_tip.x - middle_tip.x):
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_s(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """S: Closed fist with thumb across fingers"""
        score = 0.0
        
        # All fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:]):
            score += 0.4
        
        # Thumb across palm
        if analysis.thumb_position == ThumbPosition.ACROSS_PALM:
            score += 0.4
        elif not analysis.fingers[0].is_extended:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_t(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """T: Fist with thumb between index and middle"""
        score = 0.0
        
        # All fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:]):
            score += 0.35
        
        # Thumb between index and middle
        thumb_tip = landmarks[self.THUMB_TIP]
        index_pip = landmarks[self.INDEX_PIP]
        middle_pip = landmarks[self.MIDDLE_PIP]
        
        # Check thumb position between fingers
        if (min(index_pip.x, middle_pip.x) < thumb_tip.x < max(index_pip.x, middle_pip.x)):
            score += 0.35
        
        # Thumb pointing up slightly
        if thumb_tip.y < index_pip.y:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_u(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """U: Index and middle together, pointing up"""
        score = 0.0
        
        # Index and middle extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended:
            score += 0.35
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.25
        
        # Fingers together (not spread)
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        if self._distance(index_tip, middle_tip) < 35:
            score += 0.25
        
        # Pointing up
        index_mcp = landmarks[self.INDEX_MCP]
        if index_tip.y < index_mcp.y:
            score += 0.15
        
        return min(score, 1.0)
    
    def _check_v(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """V: Index and middle apart (peace sign)"""
        score = 0.0
        
        # Index and middle extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended:
            score += 0.35
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.2
        
        # Thumb curled
        if not analysis.fingers[0].is_extended:
            score += 0.1
        
        # Fingers spread apart (V shape)
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        if self._distance(index_tip, middle_tip) > 50:
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_w(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """W: Index, middle, ring extended apart"""
        score = 0.0
        
        # Three fingers extended
        if all(f.is_extended for f in analysis.fingers[1:4]):
            score += 0.4
        
        # Pinky curled
        if analysis.fingers[4].curl_state == FingerState.CURLED:
            score += 0.2
        
        # Thumb curled
        if not analysis.fingers[0].is_extended:
            score += 0.1
        
        # Fingers spread
        if analysis.finger_spread > 1.5:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_x(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """X: Index finger crooked/hooked"""
        score = 0.0
        
        # Index half-curled (crooked)
        if analysis.fingers[1].curl_state == FingerState.HALF_CURLED:
            score += 0.4
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.3
        
        # Thumb curled or beside
        if not analysis.fingers[0].is_extended:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_y(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Y: Thumb and pinky extended (hang loose)"""
        score = 0.0
        
        # Thumb extended
        if analysis.fingers[0].is_extended:
            score += 0.3
        
        # Pinky extended
        if analysis.fingers[4].is_extended:
            score += 0.3
        
        # Middle three fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:4]):
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_z(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Z: Index pointing, draw Z (motion-based, similar to 1/D statically)"""
        # Z is motion-based, statically similar to pointing
        score = 0.0
        
        # Index extended
        if analysis.fingers[1].is_extended:
            score += 0.35
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.3
        
        return min(score * 0.8, 1.0)  # Lower confidence since it's motion-based
    
    # ============== NUMBER DETECTION METHODS ==============
    
    def _check_number(self, number: str, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Check if hand matches a specific number"""
        method_name = f'_check_num_{number}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(analysis, landmarks)
        return 0.0
    
    def _check_num_0(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """0: Same as letter O"""
        return self._check_o(analysis, landmarks)
    
    def _check_num_1(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """1: Index finger only"""
        score = 0.0
        
        # Only index extended
        if analysis.fingers[1].is_extended:
            score += 0.45
        
        # All others curled
        if not analysis.fingers[0].is_extended:
            score += 0.15
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:]):
            score += 0.35
        
        return min(score, 1.0)
    
    def _check_num_2(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """2: Index and middle (same as V)"""
        return self._check_v(analysis, landmarks)
    
    def _check_num_3(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """3: Thumb, index, and middle extended"""
        score = 0.0
        
        # Thumb extended
        if analysis.fingers[0].is_extended:
            score += 0.25
        
        # Index and middle extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended:
            score += 0.35
        
        # Ring and pinky curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[3:]):
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_num_4(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """4: Four fingers extended, thumb tucked"""
        score = 0.0
        
        # Four fingers extended
        if all(f.is_extended for f in analysis.fingers[1:]):
            score += 0.5
        
        # Thumb curled across palm
        if not analysis.fingers[0].is_extended:
            score += 0.25
        if analysis.thumb_position == ThumbPosition.ACROSS_PALM:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_num_5(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """5: All fingers and thumb extended (open palm)"""
        score = 0.0
        
        # All fingers extended
        extended_count = sum(1 for f in analysis.fingers if f.is_extended)
        score += extended_count * 0.18
        
        # Fingers spread
        if analysis.finger_spread > 1.3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_num_6(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """6: Thumb and pinky extended, thumb touches middle three"""
        score = 0.0
        
        # Pinky extended
        if analysis.fingers[4].is_extended:
            score += 0.3
        
        # Thumb extended or touching
        if analysis.thumb_position == ThumbPosition.TOUCHING_FINGER:
            score += 0.35
        
        # Middle three half-curled
        mid_curled = sum(1 for f in analysis.fingers[1:4] 
                        if f.curl_state in [FingerState.HALF_CURLED, FingerState.CURLED])
        score += mid_curled * 0.1
        
        return min(score, 1.0)
    
    def _check_num_7(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """7: Thumb touches ring, others extended"""
        score = 0.0
        
        # Index, middle, pinky extended
        if analysis.fingers[1].is_extended and analysis.fingers[2].is_extended and analysis.fingers[4].is_extended:
            score += 0.35
        
        # Ring curled (thumb touching)
        if analysis.fingers[3].curl_state == FingerState.CURLED:
            score += 0.25
        
        # Thumb-ring touching
        if analysis.fingers_touching.get('thumb_ring', False):
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_num_8(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """8: Thumb touches middle, others extended"""
        score = 0.0
        
        # Index, ring, pinky extended
        if analysis.fingers[1].is_extended and analysis.fingers[3].is_extended and analysis.fingers[4].is_extended:
            score += 0.35
        
        # Middle curled (thumb touching)
        if analysis.fingers[2].curl_state == FingerState.CURLED:
            score += 0.25
        
        # Thumb-middle touching
        if analysis.fingers_touching.get('thumb_middle', False):
            score += 0.3
        
        return min(score, 1.0)
    
    def _check_num_9(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """9: Thumb and index circle, others extended"""
        score = 0.0
        
        # Middle, ring, pinky extended
        if all(f.is_extended for f in analysis.fingers[2:]):
            score += 0.35
        
        # Thumb-index touching
        if analysis.fingers_touching.get('thumb_index', False):
            score += 0.35
        
        # Index curled to meet thumb
        if not analysis.fingers[1].is_extended:
            score += 0.2
        
        return min(score, 1.0)
    
    # ============== GESTURE DETECTION METHODS ==============
    
    def _check_thumbs_up(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Thumbs up gesture"""
        score = 0.0
        
        # Thumb extended and pointing up
        if analysis.fingers[0].is_extended:
            score += 0.3
        if analysis.thumb_position == ThumbPosition.EXTENDED_UP:
            score += 0.3
        
        # Other fingers curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[1:]):
            score += 0.35
        
        return min(score, 1.0)
    
    def _check_wave(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Open palm wave"""
        return self._check_num_5(analysis, landmarks)
    
    def _check_ok(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """OK gesture (thumb-index circle)"""
        return self._check_f(analysis, landmarks)
    
    def _check_peace(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Peace sign"""
        return self._check_v(analysis, landmarks)
    
    def _check_rock(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Rock sign (index and pinky extended)"""
        score = 0.0
        
        # Index and pinky extended
        if analysis.fingers[1].is_extended and analysis.fingers[4].is_extended:
            score += 0.4
        
        # Middle and ring curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:4]):
            score += 0.35
        
        # Thumb position varies
        score += 0.15
        
        return min(score, 1.0)
    
    def _check_call(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """Call me gesture (thumb and pinky)"""
        return self._check_y(analysis, landmarks)
    
    def _check_love(self, analysis: HandAnalysis, landmarks: List[Landmark]) -> float:
        """I love you sign (thumb, index, pinky)"""
        score = 0.0
        
        # Thumb, index, pinky extended
        if analysis.fingers[0].is_extended and analysis.fingers[1].is_extended and analysis.fingers[4].is_extended:
            score += 0.5
        
        # Middle and ring curled
        if all(f.curl_state == FingerState.CURLED for f in analysis.fingers[2:4]):
            score += 0.4
        
        return min(score, 1.0)
    
    @staticmethod
    def _distance(p1: Landmark, p2: Landmark) -> float:
        """Calculate 3D Euclidean distance between two landmarks"""
        return math.sqrt(
            (p2.x - p1.x) ** 2 +
            (p2.y - p1.y) ** 2 +
            (p2.z - p1.z) ** 2
        )


# Global detector instance
sign_detector = AdvancedSignDetector()


def detect_sign(landmarks: List[List[float]]) -> Optional[DetectionResult]:
    """
    Public API to detect ASL sign from landmarks.
    
    Args:
        landmarks: 21 hand landmarks with [x, y, z] coordinates
        
    Returns:
        DetectionResult with sign, confidence, category, and metadata
    """
    return sign_detector.detect(landmarks)
