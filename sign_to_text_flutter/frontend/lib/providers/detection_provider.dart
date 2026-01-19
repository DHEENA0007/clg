import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

/// Provider for sign detection state
class DetectionProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final WebSocketService _wsService = WebSocketService();
  
  // Detection state
  bool _isDetecting = false;
  bool _isCameraOn = false;
  DetectionResult? _currentDetection;
  String _recognizedText = '';
  List<GestureData> _gestureHistory = [];
  
  // Stability tracking
  final List<String> _recentDetections = [];
  static const int _stabilityThreshold = 5;
  static const Duration _cooldownDuration = Duration(seconds: 2);
  DateTime? _lastCaptureTime;
  
  // Stats
  int _totalDetections = 0;
  double _averageConfidence = 0.0;

  // Getters
  bool get isDetecting => _isDetecting;
  bool get isCameraOn => _isCameraOn;
  DetectionResult? get currentDetection => _currentDetection;
  String get recognizedText => _recognizedText;
  List<GestureData> get gestureHistory => _gestureHistory;
  int get totalDetections => _totalDetections;
  double get averageConfidence => _averageConfidence;
  bool get isConnected => _wsService.isConnected;

  /// Start detection
  Future<void> startDetection() async {
    _isDetecting = true;
    _isCameraOn = true;
    notifyListeners();

    // Try to connect to WebSocket
    await _wsService.connect();
    
    // Listen to WebSocket detections
    _wsService.detectionStream.listen((result) {
      _handleDetection(result);
    });
  }

  /// Stop detection
  void stopDetection() {
    _isDetecting = false;
    notifyListeners();
  }

  /// Toggle camera
  void toggleCamera() {
    _isCameraOn = !_isCameraOn;
    if (!_isCameraOn) {
      _isDetecting = false;
    }
    notifyListeners();
  }

  /// Process landmarks for detection (HTTP fallback)
  Future<void> processLandmarks(List<List<double>> landmarks, {String? userId}) async {
    if (!_isDetecting) return;

    try {
      // Use WebSocket if connected, otherwise HTTP
      if (_wsService.isConnected) {
        _wsService.detectSign(landmarks);
      } else {
        final result = await _apiService.detectSign(landmarks, userId: userId);
        if (result != null) {
          _handleDetection(result);
        }
      }
    } catch (e) {
      print('Detection error: $e');
    }
  }

  /// Process camera frame image for server-side detection
  /// This sends the base64 encoded image to the backend for processing
  Future<void> processImage(String base64Image, {String? userId}) async {
    if (!_isDetecting) return;

    try {
      final result = await _apiService.detectFromImage(base64Image, userId: userId);
      if (result != null) {
        _handleDetection(result);
      }
    } catch (e) {
      print('Image detection error: $e');
    }
  }

  /// Handle detection result
  void _handleDetection(DetectionResult result) {
    _currentDetection = result;
    
    if (!result.detected || result.sign == null) {
      notifyListeners();
      return;
    }

    final confidence = result.confidence ?? 0.0;
    
    // Only process if confidence is above threshold
    if (confidence < 0.65) {
      notifyListeners();
      return;
    }

    // Add to recent detections for stability check
    _recentDetections.add(result.sign!);
    if (_recentDetections.length > _stabilityThreshold + 5) {
      _recentDetections.removeAt(0);
    }

    // Check stability (same gesture detected multiple times)
    final recentSame = _recentDetections
        .skip(_recentDetections.length > _stabilityThreshold 
            ? _recentDetections.length - _stabilityThreshold 
            : 0)
        .every((s) => s == result.sign);

    // Check cooldown
    final now = DateTime.now();
    final canCapture = _lastCaptureTime == null ||
        now.difference(_lastCaptureTime!) > _cooldownDuration;

    if (recentSame && canCapture) {
      // Capture the gesture!
      _captureGesture(result);
      _lastCaptureTime = now;
      _recentDetections.clear();
    }

    notifyListeners();
  }

  /// Capture a confirmed gesture
  void _captureGesture(DetectionResult result) {
    if (result.sign == null) return;

    // Add to recognized text
    _recognizedText += result.sign!;
    
    // Add to history
    _gestureHistory.add(GestureData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      detectedSign: result.sign!,
      confidence: result.confidence ?? 0.0,
      handShape: result.handShape,
      timestamp: DateTime.now(),
    ));

    // Update stats
    _totalDetections++;
    _averageConfidence = ((_averageConfidence * (_totalDetections - 1)) + 
        (result.confidence ?? 0.0)) / _totalDetections;

    notifyListeners();
  }

  /// Add space to recognized text
  void addSpace() {
    _recognizedText += ' ';
    notifyListeners();
  }

  /// Clear recognized text
  void clearText() {
    _recognizedText = '';
    notifyListeners();
  }

  /// Backspace
  void backspace() {
    if (_recognizedText.isNotEmpty) {
      _recognizedText = _recognizedText.substring(0, _recognizedText.length - 1);
      notifyListeners();
    }
  }

  /// Clear all data
  void clearAll() {
    _recognizedText = '';
    _gestureHistory.clear();
    _recentDetections.clear();
    _currentDetection = null;
    _totalDetections = 0;
    _averageConfidence = 0.0;
    notifyListeners();
  }

  @override
  void dispose() {
    _wsService.dispose();
    super.dispose();
  }
}
