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
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E21),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            _buildHeader(context),

            // Camera View
            Expanded(
              flex: 3,
              child: _buildCameraView(context),
            ),

            // Text Display
            Expanded(
              flex: 1,
              child: _buildTextDisplay(context),
            ),

            // Control Panel
            _buildControlPanel(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.arrow_back, color: Colors.white),
            ),
            onPressed: () => Navigator.pop(context),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Sign Detection',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                ),
                Consumer<DetectionProvider>(
                  builder: (context, provider, _) {
                    return Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: provider.isDetecting
                                ? Colors.green
                                : Colors.orange,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          provider.isDetecting
                              ? 'Detection Active'
                              : 'Detection Paused',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Colors.white60,
                                  ),
                        ),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.flip_camera_ios, color: Colors.white),
            ),
            onPressed: _switchCamera,
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildCameraView(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
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
        borderRadius: BorderRadius.circular(22),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Camera Preview
            if (_isInitialized && _controller != null)
              CameraPreview(_controller!)
            else
              Container(
                color: const Color(0xFF1D1E33),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(
                        color: Color(0xFF6C63FF),
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Initializing camera...',
                        style: TextStyle(color: Colors.white60),
                      ),
                    ],
                  ),
                ),
              ),

            // Detection Overlay
            const DetectionOverlay(),

            // Corner Guide
            _buildCornerGuides(),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 100.ms, duration: 400.ms).scale(
          begin: const Offset(0.95, 0.95),
          end: const Offset(1.0, 1.0),
        );
  }

  Widget _buildCornerGuides() {
    return LayoutBuilder(
      builder: (context, constraints) {
        const size = 40.0;
        const thickness = 3.0;
        const color = Color(0xFF6C63FF);
        const radius = 22.0;

        return Stack(
          children: [
            // Top Left
            Positioned(
              top: 0,
              left: 0,
              child: _buildCorner(
                size,
                thickness,
                color,
                topLeft: radius,
              ),
            ),
            // Top Right
            Positioned(
              top: 0,
              right: 0,
              child: Transform.flip(
                flipX: true,
                child: _buildCorner(
                  size,
                  thickness,
                  color,
                  topLeft: radius,
                ),
              ),
            ),
            // Bottom Left
            Positioned(
              bottom: 0,
              left: 0,
              child: Transform.flip(
                flipY: true,
                child: _buildCorner(
                  size,
                  thickness,
                  color,
                  topLeft: radius,
                ),
              ),
            ),
            // Bottom Right
            Positioned(
              bottom: 0,
              right: 0,
              child: Transform.flip(
                flipX: true,
                flipY: true,
                child: _buildCorner(
                  size,
                  thickness,
                  color,
                  topLeft: radius,
                ),
              ),
            ),
          ],
        );
      },
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

  Widget _buildTextDisplay(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 16),
      child: TextDisplayWidget(),
    ).animate().fadeIn(delay: 200.ms, duration: 400.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildControlPanel(BuildContext context) {
    return const ControlPanelWidget()
        .animate()
        .fadeIn(delay: 300.ms, duration: 400.ms)
        .slideY(begin: 0.2, end: 0);
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
