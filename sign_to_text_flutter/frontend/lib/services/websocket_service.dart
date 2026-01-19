import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/models.dart';

/// WebSocket service for real-time sign detection
class WebSocketService {
  static const String wsUrl = 'ws://localhost:8000/ws/detection/';
  
  WebSocketChannel? _channel;
  StreamController<DetectionResult>? _detectionController;
  bool _isConnected = false;

  bool get isConnected => _isConnected;

  Stream<DetectionResult> get detectionStream {
    _detectionController ??= StreamController<DetectionResult>.broadcast();
    return _detectionController!.stream;
  }

  /// Connect to WebSocket server
  Future<bool> connect() async {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (data) {
          final json = jsonDecode(data);
          if (json['type'] == 'detection_result') {
            final result = DetectionResult.fromJson(json);
            _detectionController?.add(result);
          }
        },
        onError: (error) {
          print('WebSocket error: $error');
          _isConnected = false;
        },
        onDone: () {
          print('WebSocket connection closed');
          _isConnected = false;
        },
      );

      _isConnected = true;
      return true;
    } catch (e) {
      print('WebSocket connection failed: $e');
      return false;
    }
  }

  /// Send landmarks for detection
  void detectSign(List<List<double>> landmarks) {
    if (!_isConnected || _channel == null) return;

    _channel!.sink.add(jsonEncode({
      'type': 'detect',
      'landmarks': landmarks,
      'timestamp': DateTime.now().toIso8601String(),
    }));
  }

  /// Send ping to keep connection alive
  void ping() {
    if (!_isConnected || _channel == null) return;
    _channel!.sink.add(jsonEncode({'type': 'ping'}));
  }

  /// Disconnect from WebSocket
  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _detectionController?.close();
  }
}
