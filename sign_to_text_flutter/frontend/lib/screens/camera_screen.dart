import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:camera/camera.dart';
import '../providers/detection_provider.dart';
import '../providers/user_provider.dart';
import '../widgets/detection_overlay.dart';
import '../widgets/text_display.dart';
import '../widgets/control_panel.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  bool _isProcessing = false;
  int _selectedCameraIndex = 0;
  Timer? _captureTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _captureTimer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_controller == null || !_controller!.value.isInitialized) return;

    if (state == AppLifecycleState.inactive) {
      _controller?.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _initializeCamera();
    }
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
        _showError('No cameras available');
        return;
      }

      // Find front camera
      _selectedCameraIndex = _cameras!.indexWhere(
        (cam) => cam.lensDirection == CameraLensDirection.front,
      );
      if (_selectedCameraIndex < 0) _selectedCameraIndex = 0;

      await _setupCamera(_selectedCameraIndex);
    } catch (e) {
      _showError('Failed to initialize camera: $e');
    }
  }

  Future<void> _setupCamera(int index) async {
    if (_cameras == null || _cameras!.isEmpty) return;

    _controller?.dispose();
    
    _controller = CameraController(
      _cameras![index],
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );

    try {
      await _controller!.initialize();
      if (!mounted) return;

      setState(() {
        _isInitialized = true;
      });

      // Start detection
      final provider = Provider.of<DetectionProvider>(context, listen: false);
      await provider.startDetection();
      
      // Start frame capture timer for server-side detection
      _startFrameCapture();
    } catch (e) {
      _showError('Camera error: $e');
    }
  }
  
  /// Start periodic frame capture for detection
  void _startFrameCapture() {
    _captureTimer?.cancel();
    
    // Capture a frame every 500ms (2 FPS) to avoid overwhelming the server
    _captureTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      _captureAndProcessFrame();
    });
  }
  
  /// Capture current frame and send for detection
  Future<void> _captureAndProcessFrame() async {
    if (!_isInitialized || _controller == null || _isProcessing) return;
    
    final provider = Provider.of<DetectionProvider>(context, listen: false);
    if (!provider.isDetecting) return;
    
    _isProcessing = true;
    
    try {
      // Take a picture
      final XFile imageFile = await _controller!.takePicture();
      
      // Read and convert to base64
      final bytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(bytes);
      
      // Get user ID if available
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      final userId = userProvider.deviceId;
      
      // Send to backend for detection
      await provider.processImage(base64Image, userId: userId);
      
    } catch (e) {
      // Silently fail - don't spam errors for frame capture issues
      debugPrint('Frame capture error: $e');
    } finally {
      _isProcessing = false;
    }
  }

  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  Future<void> _switchCamera() async {
    if (_cameras == null || _cameras!.length < 2) return;
    
    _selectedCameraIndex = (_selectedCameraIndex + 1) % _cameras!.length;
    await _setupCamera(_selectedCameraIndex);
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 380;
    final bottomPadding = MediaQuery.of(context).padding.bottom;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E21),
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            // Header
            _buildHeader(context, isSmallScreen),

            // Camera View - Takes most of the space
            Expanded(
              flex: 5,
              child: _buildCameraView(context, isSmallScreen),
            ),

            // Text Display - Compact area
            Expanded(
              flex: 2,
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: isSmallScreen ? 12 : 16),
                child: const TextDisplayWidget(),
              ),
            ),

            // Control Panel - Fixed at bottom
            Padding(
              padding: EdgeInsets.only(bottom: bottomPadding > 0 ? bottomPadding : 8),
              child: ControlPanelWidget(compact: isSmallScreen),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, bool isSmallScreen) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isSmallScreen ? 8 : 12,
        vertical: isSmallScreen ? 8 : 12,
      ),
      child: Row(
        children: [
          IconButton(
            icon: Container(
              padding: EdgeInsets.all(isSmallScreen ? 6 : 8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(Icons.arrow_back, color: Colors.white, size: isSmallScreen ? 20 : 24),
            ),
            onPressed: () => Navigator.pop(context),
          ),
          SizedBox(width: isSmallScreen ? 8 : 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Sign Detection',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        fontSize: isSmallScreen ? 16 : 18,
                      ),
                ),
                Consumer<DetectionProvider>(
                  builder: (context, provider, _) {
                    return Row(
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: provider.isDetecting ? Colors.green : Colors.orange,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          provider.isDetecting ? 'Active' : 'Paused',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.white60,
                                fontSize: isSmallScreen ? 11 : 13,
                              ),
                        ),
                        if (provider.lastDetectedSign.isNotEmpty) ...[
                          const SizedBox(width: 12),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF6C63FF).withOpacity(0.3),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              provider.lastDetectedSign,
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: isSmallScreen ? 12 : 14,
                              ),
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
          IconButton(
            icon: Container(
              padding: EdgeInsets.all(isSmallScreen ? 6 : 8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(Icons.flip_camera_ios, color: Colors.white, size: isSmallScreen ? 20 : 24),
            ),
            onPressed: _switchCamera,
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildCameraView(BuildContext context, bool isSmallScreen) {
    return Container(
      margin: EdgeInsets.symmetric(
        horizontal: isSmallScreen ? 12 : 16,
        vertical: isSmallScreen ? 8 : 12,
      ),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(isSmallScreen ? 20 : 24),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6C63FF).withOpacity(0.2),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(isSmallScreen ? 18 : 22),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Camera Preview
            if (_isInitialized && _controller != null)
              CameraPreview(_controller!)
            else
              Container(
                color: const Color(0xFF1D1E33),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox(
                        width: isSmallScreen ? 36 : 44,
                        height: isSmallScreen ? 36 : 44,
                        child: const CircularProgressIndicator(
                          color: Color(0xFF6C63FF),
                          strokeWidth: 3,
                        ),
                      ),
                      SizedBox(height: isSmallScreen ? 12 : 16),
                      Text(
                        'Initializing camera...',
                        style: TextStyle(
                          color: Colors.white60,
                          fontSize: isSmallScreen ? 13 : 15,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Detection Overlay
            const DetectionOverlay(),

            // Corner Guide
            _buildCornerGuides(isSmallScreen),
            
            // Detected Sign Display (Large overlay)
            Positioned(
              top: isSmallScreen ? 12 : 16,
              left: 0,
              right: 0,
              child: Consumer<DetectionProvider>(
                builder: (context, provider, _) {
                  if (provider.lastDetectedSign.isEmpty) return const SizedBox.shrink();
                  
                  return Center(
                    child: Container(
                      padding: EdgeInsets.symmetric(
                        horizontal: isSmallScreen ? 16 : 20,
                        vertical: isSmallScreen ? 8 : 12,
                      ),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            const Color(0xFF6C63FF).withOpacity(0.9),
                            const Color(0xFF00D9FF).withOpacity(0.9),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF6C63FF).withOpacity(0.4),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            provider.lastEmoji ?? '🤟',
                            style: TextStyle(fontSize: isSmallScreen ? 24 : 28),
                          ),
                          SizedBox(width: isSmallScreen ? 8 : 12),
                          Text(
                            provider.lastDetectedSign,
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: isSmallScreen ? 28 : 36,
                            ),
                          ),
                        ],
                      ),
                    ).animate(
                      onPlay: (controller) => controller.repeat(reverse: true),
                    ).scale(
                      begin: const Offset(1.0, 1.0),
                      end: const Offset(1.05, 1.05),
                      duration: 800.ms,
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 100.ms, duration: 400.ms).scale(
          begin: const Offset(0.95, 0.95),
          end: const Offset(1.0, 1.0),
        );
  }

  Widget _buildCornerGuides(bool isSmallScreen) {
    final size = isSmallScreen ? 32.0 : 40.0;
    const thickness = 3.0;
    const color = Color(0xFF6C63FF);
    final radius = isSmallScreen ? 18.0 : 22.0;

    return Stack(
      children: [
        // Top Left
        Positioned(
          top: 0,
          left: 0,
          child: _buildCorner(size, thickness, color, topLeft: radius),
        ),
        // Top Right
        Positioned(
          top: 0,
          right: 0,
          child: Transform.flip(
            flipX: true,
            child: _buildCorner(size, thickness, color, topLeft: radius),
          ),
        ),
        // Bottom Left
        Positioned(
          bottom: 0,
          left: 0,
          child: Transform.flip(
            flipY: true,
            child: _buildCorner(size, thickness, color, topLeft: radius),
          ),
        ),
        // Bottom Right
        Positioned(
          bottom: 0,
          right: 0,
          child: Transform.flip(
            flipX: true,
            flipY: true,
            child: _buildCorner(size, thickness, color, topLeft: radius),
          ),
        ),
      ],
    );
  }

  Widget _buildCorner(
    double size,
    double thickness,
    Color color, {
    double topLeft = 0,
  }) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: CornerPainter(
          color: color,
          thickness: thickness,
          radius: topLeft,
        ),
      ),
    );
  }
}

class CornerPainter extends CustomPainter {
  final Color color;
  final double thickness;
  final double radius;

  CornerPainter({
    required this.color,
    required this.thickness,
    required this.radius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = thickness
      ..strokeCap = StrokeCap.round;

    final path = Path()
      ..moveTo(0, size.height * 0.6)
      ..lineTo(0, radius)
      ..arcToPoint(
        Offset(radius, 0),
        radius: Radius.circular(radius),
      )
      ..lineTo(size.width * 0.6, 0);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
