import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';
import '../providers/detection_provider.dart';
import '../widgets/feature_card.dart';
import '../widgets/stats_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 380;
    final padding = isSmallScreen ? 16.0 : 20.0;

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
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              // App Bar
              SliverAppBar(
                expandedHeight: isSmallScreen ? 100 : 120,
                floating: true,
                pinned: true,
                backgroundColor: Colors.transparent,
                flexibleSpace: FlexibleSpaceBar(
                  title: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: EdgeInsets.all(isSmallScreen ? 6 : 8),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF6C63FF), Color(0xFF00D9FF)],
                          ),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text('🤟', style: TextStyle(fontSize: isSmallScreen ? 16 : 20)),
                      ),
                      SizedBox(width: isSmallScreen ? 8 : 12),
                      Text(
                        'Sign to Text',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: isSmallScreen ? 18 : 22,
                        ),
                      ),
                    ],
                  ),
                ),
                actions: [
                  Consumer<UserProvider>(
                    builder: (context, provider, _) {
                      return IconButton(
                        icon: Container(
                          padding: EdgeInsets.all(isSmallScreen ? 6 : 8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(Icons.person_outline, size: isSmallScreen ? 20 : 24),
                        ),
                        onPressed: () {
                          _showProfileSheet(context, provider);
                        },
                      );
                    },
                  ),
                  SizedBox(width: isSmallScreen ? 4 : 8),
                ],
              ),

              // Content
              SliverPadding(
                padding: EdgeInsets.all(padding),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    // Welcome Section
                    _buildWelcomeSection(context, isSmallScreen),
                    SizedBox(height: isSmallScreen ? 20 : 28),

                    // Quick Stats
                    _buildStatsSection(context, isSmallScreen),
                    SizedBox(height: isSmallScreen ? 20 : 28),

                    // Features Grid
                    _buildFeaturesSection(context, isSmallScreen, screenSize),
                    SizedBox(height: isSmallScreen ? 20 : 28),

                    // Start Detection Button
                    _buildStartButton(context, isSmallScreen),
                    SizedBox(height: isSmallScreen ? 24 : 40),
                  ]),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(BuildContext context, bool isSmallScreen) {
    return Consumer<UserProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFF6C63FF).withOpacity(0.2),
                const Color(0xFF00D9FF).withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.all(isSmallScreen ? 8 : 10),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.check_circle, color: Colors.green, size: isSmallScreen ? 20 : 24),
                  ),
                  SizedBox(width: isSmallScreen ? 12 : 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'AI Ready',
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                                fontSize: isSmallScreen ? 16 : 18,
                              ),
                        ),
                        Text(
                          'Real-time sign language detection',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.white60,
                                fontSize: isSmallScreen ? 11 : 13,
                              ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              SizedBox(height: isSmallScreen ? 12 : 16),
              Text(
                'Welcome! Use AI to detect American Sign Language (ASL) gestures and convert them to text in real-time.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.white70,
                      height: 1.4,
                      fontSize: isSmallScreen ? 12 : 14,
                    ),
              ),
            ],
          ),
        )
            .animate()
            .fadeIn(duration: 500.ms)
            .slideX(begin: -0.1, end: 0);
      },
    );
  }

  Widget _buildStatsSection(BuildContext context, bool isSmallScreen) {
    return Consumer<DetectionProvider>(
      builder: (context, provider, _) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Your Stats',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontSize: isSmallScreen ? 16 : 18,
                  ),
            ),
            SizedBox(height: isSmallScreen ? 12 : 16),
            LayoutBuilder(
              builder: (context, constraints) {
                final cardWidth = (constraints.maxWidth - 24) / 3;
                return Row(
                  children: [
                    SizedBox(
                      width: cardWidth,
                      child: StatsCard(
                        icon: Icons.gesture,
                        iconColor: const Color(0xFF6C63FF),
                        value: provider.totalDetections.toString(),
                        label: 'Detections',
                        compact: isSmallScreen,
                      ),
                    ),
                    const SizedBox(width: 12),
                    SizedBox(
                      width: cardWidth,
                      child: StatsCard(
                        icon: Icons.analytics,
                        iconColor: const Color(0xFF00D9FF),
                        value: '${(provider.averageConfidence * 100).toStringAsFixed(0)}%',
                        label: 'Confidence',
                        compact: isSmallScreen,
                      ),
                    ),
                    const SizedBox(width: 12),
                    SizedBox(
                      width: cardWidth,
                      child: StatsCard(
                        icon: Icons.history,
                        iconColor: Colors.orange,
                        value: provider.gestureHistory.length.toString(),
                        label: 'History',
                        compact: isSmallScreen,
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        )
            .animate()
            .fadeIn(delay: 200.ms, duration: 500.ms)
            .slideY(begin: 0.1, end: 0);
      },
    );
  }

  Widget _buildFeaturesSection(BuildContext context, bool isSmallScreen, Size screenSize) {
    // Calculate optimal aspect ratio based on screen size
    final aspectRatio = isSmallScreen ? 1.0 : (screenSize.width > 400 ? 1.15 : 1.05);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Features',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: isSmallScreen ? 16 : 18,
              ),
        ),
        SizedBox(height: isSmallScreen ? 12 : 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: isSmallScreen ? 12 : 16,
          crossAxisSpacing: isSmallScreen ? 12 : 16,
          childAspectRatio: aspectRatio,
          children: [
            FeatureCard(
              icon: Icons.camera_alt,
              title: 'Sign Detection',
              description: 'Real-time ASL recognition',
              gradient: const [Color(0xFF6C63FF), Color(0xFF5A54D9)],
              onTap: () => Navigator.pushNamed(context, '/camera'),
              compact: isSmallScreen,
            ),
            FeatureCard(
              icon: Icons.text_fields,
              title: 'Text Output',
              description: 'Converted text display',
              gradient: const [Color(0xFF00D9FF), Color(0xFF00B4D8)],
              onTap: () => Navigator.pushNamed(context, '/camera'),
              compact: isSmallScreen,
            ),
            FeatureCard(
              icon: Icons.school,
              title: 'Learn ASL',
              description: 'Browse ASL alphabet',
              gradient: const [Color(0xFFFF6B6B), Color(0xFFEE5A5A)],
              onTap: () => _showAlphabetSheet(context, isSmallScreen),
              compact: isSmallScreen,
            ),
            FeatureCard(
              icon: Icons.insights,
              title: 'Analytics',
              description: 'View your progress',
              gradient: const [Color(0xFF4ECDC4), Color(0xFF44A39B)],
              onTap: () => _showStatsSheet(context),
              compact: isSmallScreen,
            ),
          ],
        ),
      ],
    )
        .animate()
        .fadeIn(delay: 400.ms, duration: 500.ms)
        .slideY(begin: 0.1, end: 0);
  }

  Widget _buildStartButton(BuildContext context, bool isSmallScreen) {
    return Center(
      child: Container(
        width: double.infinity,
        height: isSmallScreen ? 54 : 60,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF6C63FF), Color(0xFF00D9FF)],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF6C63FF).withOpacity(0.4),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.transparent,
            shadowColor: Colors.transparent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          onPressed: () => Navigator.pushNamed(context, '/camera'),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.play_arrow_rounded, size: isSmallScreen ? 26 : 30),
              SizedBox(width: isSmallScreen ? 8 : 12),
              Text(
                'Start Detection',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      fontSize: isSmallScreen ? 16 : 18,
                    ),
              ),
            ],
          ),
        ),
      ),
    )
        .animate()
        .fadeIn(delay: 600.ms, duration: 500.ms)
        .slideY(begin: 0.2, end: 0);
  }

  void _showProfileSheet(BuildContext context, UserProvider provider) {
    final isSmallScreen = MediaQuery.of(context).size.width < 380;
    
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1D1E33),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return SafeArea(
          child: Container(
            padding: EdgeInsets.all(isSmallScreen ? 16 : 24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                SizedBox(height: isSmallScreen ? 16 : 24),
                Icon(Icons.person, size: isSmallScreen ? 48 : 60, color: const Color(0xFF6C63FF)),
                SizedBox(height: isSmallScreen ? 12 : 16),
                Text(
                  'Profile',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        fontSize: isSmallScreen ? 20 : 24,
                      ),
                ),
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildProfileRow('Device ID', provider.deviceId?.substring(0, 8) ?? 'N/A', isSmallScreen),
                _buildProfileRow('Total Gestures', provider.profile?.totalGestures.toString() ?? '0', isSmallScreen),
                _buildProfileRow('Sessions', provider.profile?.sessionCount.toString() ?? '0', isSmallScreen),
                SizedBox(height: isSmallScreen ? 16 : 24),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildProfileRow(String label, String value, bool isSmallScreen) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: isSmallScreen ? 6 : 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.white60, fontSize: isSmallScreen ? 13 : 15)),
          Text(value,
              style: TextStyle(
                  color: Colors.white, 
                  fontWeight: FontWeight.bold,
                  fontSize: isSmallScreen ? 13 : 15)),
        ],
      ),
    );
  }

  void _showAlphabetSheet(BuildContext context, bool isSmallScreen) {
    final letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    final numbers = '0123456789'.split('');
    final emojis = {
      'A': '✊', 'B': '🖐️', 'C': '🤏', 'D': '☝️', 'E': '✊',
      'F': '👌', 'G': '👉', 'H': '👈', 'I': '🤙', 'J': '🤙',
      'K': '✌️', 'L': '🤟', 'M': '👊', 'N': '👊', 'O': '⭕',
      'P': '👇', 'Q': '👇', 'R': '🤞', 'S': '✊', 'T': '👊',
      'U': '🤘', 'V': '✌️', 'W': '🤟', 'X': '🤞', 'Y': '🤙', 'Z': '👉',
      '0': '👌', '1': '☝️', '2': '✌️', '3': '🤟', '4': '🖐️',
      '5': '🖐️', '6': '🤙', '7': '🤟', '8': '🤟', '9': '👌',
    };

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1D1E33),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.75,
          maxChildSize: 0.9,
          minChildSize: 0.5,
          expand: false,
          builder: (context, scrollController) {
            return SafeArea(
              child: Container(
                padding: EdgeInsets.all(isSmallScreen ? 16 : 24),
                child: Column(
                  children: [
                    Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.white24,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                    Text(
                      'ASL Alphabet & Numbers',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            fontSize: isSmallScreen ? 18 : 22,
                          ),
                    ),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                    Expanded(
                      child: ListView(
                        controller: scrollController,
                        children: [
                          // Letters section
                          Text(
                            'Letters (A-Z)',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: Colors.white70,
                                  fontSize: isSmallScreen ? 13 : 15,
                                ),
                          ),
                          const SizedBox(height: 12),
                          GridView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: isSmallScreen ? 5 : 6,
                              mainAxisSpacing: 8,
                              crossAxisSpacing: 8,
                            ),
                            itemCount: letters.length,
                            itemBuilder: (context, index) {
                              final letter = letters[index];
                              return _buildSignTile(letter, emojis[letter] ?? '👋', isSmallScreen);
                            },
                          ),
                          SizedBox(height: isSmallScreen ? 16 : 24),
                          // Numbers section
                          Text(
                            'Numbers (0-9)',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: Colors.white70,
                                  fontSize: isSmallScreen ? 13 : 15,
                                ),
                          ),
                          const SizedBox(height: 12),
                          GridView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: 5,
                              mainAxisSpacing: 8,
                              crossAxisSpacing: 8,
                            ),
                            itemCount: numbers.length,
                            itemBuilder: (context, index) {
                              final number = numbers[index];
                              return _buildSignTile(number, emojis[number] ?? '👋', isSmallScreen);
                            },
                          ),
                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildSignTile(String character, String emoji, bool isSmallScreen) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF6C63FF).withOpacity(0.3),
            const Color(0xFF00D9FF).withOpacity(0.2),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(emoji, style: TextStyle(fontSize: isSmallScreen ? 18 : 22)),
          SizedBox(height: isSmallScreen ? 2 : 4),
          Text(
            character,
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: isSmallScreen ? 13 : 15,
            ),
          ),
        ],
      ),
    );
  }

  void _showStatsSheet(BuildContext context) {
    final isSmallScreen = MediaQuery.of(context).size.width < 380;
    
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1D1E33),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Consumer<DetectionProvider>(
          builder: (context, provider, _) {
            return SafeArea(
              child: Container(
                padding: EdgeInsets.all(isSmallScreen ? 16 : 24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.white24,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                    Icon(Icons.insights, size: isSmallScreen ? 48 : 60, color: const Color(0xFF4ECDC4)),
                    SizedBox(height: isSmallScreen ? 12 : 16),
                    Text(
                      'Analytics',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            fontSize: isSmallScreen ? 20 : 24,
                          ),
                    ),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                    _buildProfileRow('Total Detections', provider.totalDetections.toString(), isSmallScreen),
                    _buildProfileRow('Average Confidence', '${(provider.averageConfidence * 100).toStringAsFixed(1)}%', isSmallScreen),
                    _buildProfileRow('Gestures in History', provider.gestureHistory.length.toString(), isSmallScreen),
                    _buildProfileRow('Current Text Length', provider.recognizedText.length.toString(), isSmallScreen),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}
