import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/detection_provider.dart';

class ControlPanelWidget extends StatelessWidget {
  const ControlPanelWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<DetectionProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.transparent,
                const Color(0xFF0A0E21).withOpacity(0.8),
              ],
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Camera toggle
              _buildControlButton(
                context,
                icon: provider.isCameraOn
                    ? Icons.videocam
                    : Icons.videocam_off,
                label: provider.isCameraOn ? 'Camera On' : 'Camera Off',
                color: provider.isCameraOn
                    ? const Color(0xFF00D9FF)
                    : Colors.grey,
                onPressed: () => provider.toggleCamera(),
              ),

              // Main start/stop button
              _buildMainButton(context, provider),

              // Clear button
              _buildControlButton(
                context,
                icon: Icons.delete_outline,
                label: 'Clear',
                color: const Color(0xFFFF6B6B),
                onPressed: () => _showClearDialog(context, provider),
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
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: IconButton(
            icon: Icon(icon, color: color),
            onPressed: onPressed,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white60,
              ),
        ),
      ],
    );
  }

  Widget _buildMainButton(BuildContext context, DetectionProvider provider) {
    final isDetecting = provider.isDetecting;

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
            width: 80,
            height: 80,
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
                  blurRadius: 20,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Icon(
              isDetecting ? Icons.stop : Icons.play_arrow,
              color: Colors.white,
              size: 40,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          isDetecting ? 'Stop' : 'Start',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
        ),
      ],
    );
  }

  void _showClearDialog(BuildContext context, DetectionProvider provider) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF1D1E33),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Text(
            'Clear All Data?',
            style: TextStyle(color: Colors.white),
          ),
          content: const Text(
            'This will clear all recognized text and history. This action cannot be undone.',
            style: TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFF6B6B),
              ),
              onPressed: () {
                provider.clearAll();
                Navigator.pop(context);
              },
              child: const Text('Clear', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }
}
