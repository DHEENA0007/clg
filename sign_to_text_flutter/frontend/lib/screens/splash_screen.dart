import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // Initialize user provider
    final userProvider = Provider.of<UserProvider>(context, listen: false);
    await userProvider.initialize();

    // Navigate to home after delay
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 380;
    
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0A0E21),
              Color(0xFF1D1E33),
              Color(0xFF0A0E21),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: isSmallScreen ? 24 : 40),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Spacer(flex: 2),
                  
                  // Logo with animation
                  Container(
                    width: isSmallScreen ? 120 : 150,
                    height: isSmallScreen ? 120 : 150,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF6C63FF), Color(0xFF00D9FF)],
                      ),
                      borderRadius: BorderRadius.circular(isSmallScreen ? 32 : 40),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF6C63FF).withOpacity(0.4),
                          blurRadius: 30,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        '🤟',
                        style: TextStyle(fontSize: isSmallScreen ? 64 : 80),
                      ),
                    ),
                  )
                      .animate()
                      .scale(
                        begin: const Offset(0.5, 0.5),
                        end: const Offset(1.0, 1.0),
                        duration: 600.ms,
                        curve: Curves.easeOutBack,
                      )
                      .fadeIn(duration: 500.ms),

                  SizedBox(height: isSmallScreen ? 32 : 40),

                  // Title
                  Text(
                    'Sign to Text',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontSize: isSmallScreen ? 28 : 34,
                        ),
                  )
                      .animate()
                      .fadeIn(delay: 300.ms, duration: 500.ms)
                      .slideY(begin: 0.3, end: 0),

                  SizedBox(height: isSmallScreen ? 8 : 12),

                  // Subtitle
                  Text(
                    'AI-Powered Sign Language Detection',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.white60,
                          fontSize: isSmallScreen ? 14 : 16,
                        ),
                  )
                      .animate()
                      .fadeIn(delay: 500.ms, duration: 500.ms)
                      .slideY(begin: 0.3, end: 0),

                  const Spacer(flex: 1),

                  // Features preview
                  Container(
                    padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white.withOpacity(0.1)),
                    ),
                    child: Column(
                      children: [
                        _buildFeatureRow(
                          Icons.camera_alt,
                          'Real-time hand detection',
                          isSmallScreen,
                        ),
                        SizedBox(height: isSmallScreen ? 12 : 16),
                        _buildFeatureRow(
                          Icons.text_fields,
                          'ASL to text conversion',
                          isSmallScreen,
                        ),
                        SizedBox(height: isSmallScreen ? 12 : 16),
                        _buildFeatureRow(
                          Icons.speed,
                          'Fast & accurate AI',
                          isSmallScreen,
                        ),
                      ],
                    ),
                  )
                      .animate()
                      .fadeIn(delay: 700.ms, duration: 500.ms)
                      .slideY(begin: 0.2, end: 0),

                  const Spacer(flex: 1),

                  // Loading indicator
                  SizedBox(
                    width: isSmallScreen ? 32 : 40,
                    height: isSmallScreen ? 32 : 40,
                    child: const CircularProgressIndicator(
                      strokeWidth: 3,
                      valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF6C63FF)),
                    ),
                  ).animate().fadeIn(delay: 900.ms, duration: 300.ms),

                  SizedBox(height: isSmallScreen ? 12 : 16),

                  Text(
                    'Initializing...',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.white38,
                          fontSize: isSmallScreen ? 12 : 14,
                        ),
                  ).animate().fadeIn(delay: 1000.ms, duration: 300.ms),
                  
                  const Spacer(flex: 1),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureRow(IconData icon, String text, bool isSmallScreen) {
    return Row(
      children: [
        Container(
          padding: EdgeInsets.all(isSmallScreen ? 8 : 10),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFF6C63FF).withOpacity(0.3),
                const Color(0xFF00D9FF).withOpacity(0.2),
              ],
            ),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: const Color(0xFF00D9FF),
            size: isSmallScreen ? 18 : 22,
          ),
        ),
        SizedBox(width: isSmallScreen ? 12 : 16),
        Expanded(
          child: Text(
            text,
            style: TextStyle(
              color: Colors.white70,
              fontSize: isSmallScreen ? 13 : 15,
            ),
          ),
        ),
      ],
    );
  }
}
