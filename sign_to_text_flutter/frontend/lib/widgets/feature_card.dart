import 'package:flutter/material.dart';

class FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final List<Color> gradient;
  final VoidCallback? onTap;
  final bool compact;

  const FeatureCard({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
    required this.gradient,
    this.onTap,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(compact ? 12 : 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              gradient[0].withOpacity(0.3),
              gradient[1].withOpacity(0.1),
            ],
          ),
          borderRadius: BorderRadius.circular(compact ? 16 : 20),
          border: Border.all(
            color: gradient[0].withOpacity(0.3),
          ),
          boxShadow: [
            BoxShadow(
              color: gradient[0].withOpacity(0.1),
              blurRadius: compact ? 12 : 20,
              offset: Offset(0, compact ? 6 : 10),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: EdgeInsets.all(compact ? 8 : 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: gradient),
                borderRadius: BorderRadius.circular(compact ? 10 : 14),
              ),
              child: Icon(icon, color: Colors.white, size: compact ? 22 : 28),
            ),
            const Spacer(),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontSize: compact ? 14 : 16,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            SizedBox(height: compact ? 2 : 4),
            Text(
              description,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white60,
                    fontSize: compact ? 11 : 13,
                  ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
