import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/detection_provider.dart';

class ControlPanelWidget extends StatelessWidget {
  final bool compact;

  const ControlPanelWidget({super.key, this.compact = false});

  @override
  Widget build(BuildContext context) {
    return Consumer<DetectionProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 16 : 20,
            vertical: compact ? 12 : 16,
          ),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.transparent,
                const Color(0xFF0A0E21).withOpacity(0.9),
              ],
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Camera toggle
              _buildControlButton(
                context,
                icon: provider.isCameraOn ? Icons.videocam : Icons.videocam_off,
                label: provider.isCameraOn ? 'On' : 'Off',
                color: provider.isCameraOn ? const Color(0xFF00D9FF) : Colors.grey,
                onPressed: () => provider.toggleCamera(),
                compact: compact,
              ),

              // Main start/stop button
              _buildMainButton(context, provider, compact),

              // Clear button
              _buildControlButton(
                context,
                icon: Icons.delete_outline,
                label: 'Clear',
                color: const Color(0xFFFF6B6B),
                onPressed: () => _showClearDialog(context, provider),
                compact: compact,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildControlButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onPressed,
    required bool compact,
  }) {
    final buttonSize = compact ? 48.0 : 56.0;
    final iconSize = compact ? 22.0 : 26.0;
    final fontSize = compact ? 10.0 : 12.0;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(compact ? 12 : 16),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: IconButton(
            icon: Icon(icon, color: color, size: iconSize),
            onPressed: onPressed,
            padding: EdgeInsets.zero,
          ),
        ),
        SizedBox(height: compact ? 4 : 8),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white60,
                fontSize: fontSize,
              ),
        ),
      ],
    );
  }

  Widget _buildMainButton(BuildContext context, DetectionProvider provider, bool compact) {
    final isDetecting = provider.isDetecting;
    final buttonSize = compact ? 64.0 : 80.0;
    final iconSize = compact ? 32.0 : 40.0;
    final fontSize = compact ? 12.0 : 14.0;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: () {
            if (isDetecting) {
              provider.stopDetection();
            } else {
              provider.startDetection();
            }
          },
          child: Container(
            width: buttonSize,
            height: buttonSize,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDetecting
                    ? [const Color(0xFFFF6B6B), const Color(0xFFEE5A5A)]
                    : [const Color(0xFF6C63FF), const Color(0xFF00D9FF)],
              ),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: (isDetecting
                          ? const Color(0xFFFF6B6B)
                          : const Color(0xFF6C63FF))
                      .withOpacity(0.4),
                  blurRadius: compact ? 12 : 20,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Icon(
              isDetecting ? Icons.stop : Icons.play_arrow,
              color: Colors.white,
              size: iconSize,
            ),
          ),
        ),
        SizedBox(height: compact ? 4 : 8),
        Text(
          isDetecting ? 'Stop' : 'Start',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: fontSize,
              ),
        ),
      ],
    );
  }

  void _showClearDialog(BuildContext context, DetectionProvider provider) {
    final isSmallScreen = MediaQuery.of(context).size.width < 380;
    
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF1D1E33),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: Text(
            'Clear All Data?',
            style: TextStyle(
              color: Colors.white,
              fontSize: isSmallScreen ? 18 : 20,
            ),
          ),
          content: Text(
            'This will clear all recognized text and history. This action cannot be undone.',
            style: TextStyle(
              color: Colors.white70,
              fontSize: isSmallScreen ? 13 : 15,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(
                'Cancel',
                style: TextStyle(fontSize: isSmallScreen ? 13 : 15),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFF6B6B),
                padding: EdgeInsets.symmetric(
                  horizontal: isSmallScreen ? 16 : 20,
                  vertical: isSmallScreen ? 8 : 12,
                ),
              ),
              onPressed: () {
                provider.clearAll();
                Navigator.pop(context);
              },
              child: Text(
                'Clear',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: isSmallScreen ? 13 : 15,
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
