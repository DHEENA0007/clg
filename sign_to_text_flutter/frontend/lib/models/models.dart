/// Detection result from the API
class DetectionResult {
  final bool detected;
  final String? sign;
  final double? confidence;
  final String? handShape;
  final String? description;
  final String? emoji;
  final String? message;

  DetectionResult({
    required this.detected,
    this.sign,
    this.confidence,
    this.handShape,
    this.description,
    this.emoji,
    this.message,
  });

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      detected: json['detected'] ?? false,
      sign: json['sign'],
      confidence: json['confidence']?.toDouble(),
      handShape: json['hand_shape'],
      description: json['description'],
      emoji: json['emoji'],
      message: json['message'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'detected': detected,
      'sign': sign,
      'confidence': confidence,
      'hand_shape': handShape,
      'description': description,
      'emoji': emoji,
      'message': message,
    };
  }
}

/// User profile for gesture tracking
class UserProfile {
  final String id;
  final String? deviceId;
  final String handSize;
  final String dominantHand;
  final int totalGestures;
  final double averageAccuracy;
  final int sessionCount;
  final DateTime createdAt;
  final DateTime updatedAt;

  UserProfile({
    required this.id,
    this.deviceId,
    this.handSize = 'medium',
    this.dominantHand = 'right',
    this.totalGestures = 0,
    this.averageAccuracy = 0.0,
    this.sessionCount = 0,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      deviceId: json['device_id'],
      handSize: json['hand_size'] ?? 'medium',
      dominantHand: json['dominant_hand'] ?? 'right',
      totalGestures: json['total_gestures'] ?? 0,
      averageAccuracy: (json['average_accuracy'] ?? 0.0).toDouble(),
      sessionCount: json['session_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_id': deviceId,
      'hand_size': handSize,
      'dominant_hand': dominantHand,
      'total_gestures': totalGestures,
      'average_accuracy': averageAccuracy,
      'session_count': sessionCount,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

/// Gesture data for a single detection
class GestureData {
  final String id;
  final String detectedSign;
  final double confidence;
  final String recognitionMethod;
  final List<List<double>>? landmarks;
  final String? handShape;
  final DateTime timestamp;
  final bool isLowConfidence;

  GestureData({
    required this.id,
    required this.detectedSign,
    required this.confidence,
    this.recognitionMethod = 'fingerpose',
    this.landmarks,
    this.handShape,
    required this.timestamp,
    this.isLowConfidence = false,
  });

  factory GestureData.fromJson(Map<String, dynamic> json) {
    return GestureData(
      id: json['id'] ?? '',
      detectedSign: json['detected_sign'] ?? json['detectedSign'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      recognitionMethod: json['recognition_method'] ?? json['recognitionMethod'] ?? 'fingerpose',
      landmarks: json['landmarks'] != null 
          ? (json['landmarks'] as List).map((l) => (l as List).map((e) => (e as num).toDouble()).toList()).toList()
          : null,
      handShape: json['hand_shape'] ?? json['handShape'],
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
      isLowConfidence: json['is_low_confidence'] ?? json['isLowConfidence'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'detected_sign': detectedSign,
      'confidence': confidence,
      'recognition_method': recognitionMethod,
      'landmarks': landmarks,
      'hand_shape': handShape,
      'timestamp': timestamp.toIso8601String(),
      'is_low_confidence': isLowConfidence,
    };
  }
}

/// ASL Sign reference data
class ASLSign {
  final String letter;
  final String description;
  final String handShape;
  final String? emoji;
  final String? imageUrl;

  ASLSign({
    required this.letter,
    required this.description,
    required this.handShape,
    this.emoji,
    this.imageUrl,
  });

  factory ASLSign.fromJson(Map<String, dynamic> json) {
    return ASLSign(
      letter: json['letter'],
      description: json['description'],
      handShape: json['hand_shape'] ?? json['handShape'] ?? '',
      emoji: json['emoji'],
      imageUrl: json['image_url'] ?? json['imageUrl'],
    );
  }
}
