import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

/// API Service for communicating with Django backend
class ApiService {
  // Change this to your Django server URL
  static const String baseUrl = 'http://localhost:8000/api';
  
  final http.Client _client = http.Client();

  /// Health check
  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/health/'),
      );
      return response.statusCode == 200;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  /// Detect sign from landmarks
  Future<DetectionResult?> detectSign(List<List<double>> landmarks, {String? userId}) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/detect/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'landmarks': landmarks,
          'user_id': userId,
          'session_context': 'flutter_app',
        }),
      );

      if (response.statusCode == 200) {
        return DetectionResult.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('Detection API error: $e');
      return null;
    }
  }

  /// Detect sign from base64 encoded camera image (server-side processing)
  Future<DetectionResult?> detectFromImage(String base64Image, {String? userId}) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/detect-image/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'image': base64Image,
          'user_id': userId,
        }),
      );

      if (response.statusCode == 200) {
        return DetectionResult.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 501) {
        // MediaPipe not available on server
        print('Server-side detection not available');
        return null;
      }
      return null;
    } catch (e) {
      print('Image detection API error: $e');
      return null;
    }
  }

  /// Get or create user profile by device ID
  Future<UserProfile?> getOrCreateProfile(String deviceId) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/users/get_or_create_by_device/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'device_id': deviceId,
          'hand_size': 'medium',
          'dominant_hand': 'right',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return UserProfile.fromJson(data['profile']);
      }
      return null;
    } catch (e) {
      print('Profile API error: $e');
      return null;
    }
  }

  /// Upload batch of gestures
  Future<bool> uploadGestures(String userId, List<GestureData> gestures) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/gestures/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'gestures': gestures.map((g) => g.toJson()).toList(),
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('Upload gestures error: $e');
      return false;
    }
  }

  /// Get gesture statistics for a user
  Future<Map<String, dynamic>?> getGestureStats(String userId) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/gestures/stats/$userId/'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['stats'];
      }
      return null;
    } catch (e) {
      print('Stats API error: $e');
      return null;
    }
  }

  /// Get personalized thresholds for a user
  Future<Map<String, double>?> getPersonalizedThresholds(String userId) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/gestures/thresholds/$userId/'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final thresholds = data['thresholds'] as Map<String, dynamic>;
        return thresholds.map((k, v) => MapEntry(k, (v as num).toDouble()));
      }
      return null;
    } catch (e) {
      print('Thresholds API error: $e');
      return null;
    }
  }

  /// Get ASL alphabet reference
  Future<List<ASLSign>?> getASLAlphabet() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/signs/alphabet/'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['alphabet'] as List)
            .map((s) => ASLSign.fromJson(s))
            .toList();
      }
      return null;
    } catch (e) {
      print('Alphabet API error: $e');
      return null;
    }
  }

  void dispose() {
    _client.close();
  }
}
