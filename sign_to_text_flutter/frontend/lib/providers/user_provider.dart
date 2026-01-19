import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import '../models/models.dart';
import '../services/api_service.dart';

/// Provider for user profile and settings
class UserProvider extends ChangeNotifier {
  UserProfile? _profile;
  bool _isLoading = false;
  String? _deviceId;
  final ApiService _apiService = ApiService();

  UserProfile? get profile => _profile;
  bool get isLoading => _isLoading;
  String? get deviceId => _deviceId;
  bool get isLoggedIn => _profile != null;

  /// Initialize user - get or create profile
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Get or generate device ID
      final prefs = await SharedPreferences.getInstance();
      _deviceId = prefs.getString('device_id');
      
      if (_deviceId == null) {
        _deviceId = const Uuid().v4();
        await prefs.setString('device_id', _deviceId!);
      }

      // Get or create profile from API
      _profile = await _apiService.getOrCreateProfile(_deviceId!);
    } catch (e) {
      print('Error initializing user: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Update hand preferences
  Future<void> updatePreferences({String? handSize, String? dominantHand}) async {
    // In a real app, this would call the API to update preferences
    notifyListeners();
  }

  /// Refresh profile from API
  Future<void> refreshProfile() async {
    if (_deviceId == null) return;
    
    _isLoading = true;
    notifyListeners();

    try {
      _profile = await _apiService.getOrCreateProfile(_deviceId!);
    } catch (e) {
      print('Error refreshing profile: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Clear local data
  Future<void> clearData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('device_id');
    _profile = null;
    _deviceId = null;
    notifyListeners();
  }
}
