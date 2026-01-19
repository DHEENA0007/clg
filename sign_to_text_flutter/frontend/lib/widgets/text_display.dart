import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/detection_provider.dart';

class TextDisplayWidget extends StatelessWidget {
  const TextDisplayWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 380;

    return Consumer<DetectionProvider>(
      builder: (context, provider, _) {
        final text = provider.recognizedText;

        return Container(
          margin: EdgeInsets.only(bottom: isSmallScreen ? 8 : 12),
          padding: EdgeInsets.all(isSmallScreen ? 12 : 16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFF6C63FF).withOpacity(0.2),
                const Color(0xFF00D9FF).withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(isSmallScreen ? 16 : 20),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.text_fields,
                        color: const Color(0xFF6C63FF),
                        size: isSmallScreen ? 16 : 20,
                      ),
                      SizedBox(width: isSmallScreen ? 6 : 8),
                      Text(
                        'Recognized Text',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              color: Colors.white70,
                              fontWeight: FontWeight.w600,
                              fontSize: isSmallScreen ? 12 : 14,
                            ),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      // Copy button
                      if (text.isNotEmpty)
                        _buildIconButton(
                          icon: Icons.copy,
                          onPressed: () => _copyToClipboard(context, text),
                          tooltip: 'Copy',
                          isSmallScreen: isSmallScreen,
                        ),
                      SizedBox(width: isSmallScreen ? 4 : 8),
                      // Clear button
                      if (text.isNotEmpty)
                        _buildIconButton(
                          icon: Icons.clear,
                          onPressed: () => provider.clearText(),
                          tooltip: 'Clear',
                          isSmallScreen: isSmallScreen,
                        ),
                    ],
                  ),
                ],
              ),
              SizedBox(height: isSmallScreen ? 8 : 12),
              
              // Text display area
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: text.isEmpty
                      ? Text(
                          'Your detected signs will appear here...',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.white38,
                                fontStyle: FontStyle.italic,
                                fontSize: isSmallScreen ? 13 : 15,
                              ),
                        )
                      : SelectableText(
                          text,
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                                letterSpacing: 1.5,
                                height: 1.4,
                                fontSize: isSmallScreen ? 20 : 24,
                              ),
                        ),
                ),
              ),
              
              SizedBox(height: isSmallScreen ? 6 : 8),
              
              // Bottom action bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${text.length} chars',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white38,
                          fontSize: isSmallScreen ? 10 : 12,
                        ),
                  ),
                  // Quick action buttons
                  Row(
                    children: [
                      _buildQuickButton(
                        context,
                        'Space',
                        Icons.space_bar,
                        () => provider.addSpace(),
                        isSmallScreen,
                      ),
                      SizedBox(width: isSmallScreen ? 6 : 8),
                      _buildQuickButton(
                        context,
                        'Back',
                        Icons.backspace_outlined,
                        () => provider.backspace(),
                        isSmallScreen,
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildIconButton({
    required IconData icon,
    required VoidCallback onPressed,
    required String tooltip,
    required bool isSmallScreen,
  }) {
    return InkWell(
      onTap: onPressed,
      borderRadius: BorderRadius.circular(6),
      child: Padding(
        padding: EdgeInsets.all(isSmallScreen ? 4 : 6),
        child: Icon(icon, size: isSmallScreen ? 16 : 18, color: Colors.white60),
      ),
    );
  }

  Widget _buildQuickButton(
    BuildContext context,
    String label,
    IconData icon,
    VoidCallback onPressed,
    bool isSmallScreen,
  ) {
    return InkWell(
      onTap: onPressed,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: isSmallScreen ? 8 : 10,
          vertical: isSmallScreen ? 4 : 6,
        ),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: isSmallScreen ? 12 : 14, color: Colors.white60),
            SizedBox(width: isSmallScreen ? 3 : 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white60,
                    fontSize: isSmallScreen ? 10 : 12,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Copied to clipboard'),
        backgroundColor: const Color(0xFF6C63FF),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: const Duration(seconds: 2),
        margin: const EdgeInsets.all(16),
      ),
    );
  }
}
