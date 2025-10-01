import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'floating_island.dart';

import 'package:hourz/shared/constants/app_routes.dart';

/// Navigation Island Widget
///
/// Pre-configured FloatingIsland with app navigation.
/// Use this widget across all screens for consistent navigation.
///
/// Example:
/// ```dart
/// Stack(
///   children: [
///     YourContent(),
///     NavigationIsland(currentRoute: '/home'),
///   ],
/// )
/// ```

class NavigationIsland extends StatelessWidget {
  /// Current route path to highlight the active item
  final String currentRoute;

  const NavigationIsland({super.key, required this.currentRoute});

  int _getCurrentIndex() {
    if (currentRoute.startsWith(AppRoutePath.dashboard) ||
        currentRoute == '/') {
      return 0;
    }
    if (currentRoute.startsWith(AppRoutePath.history)) return 1;
    if (currentRoute.startsWith(AppRoutePath.addGig)) return 2;
    if (currentRoute.startsWith(AppRoutePath.chat)) return 3;
    if (currentRoute.startsWith(AppRoutePath.profile)) return 4;
    return 0; // Default to home
  }

  @override
  Widget build(BuildContext context) {
    return FloatingIsland(
      currentIndex: _getCurrentIndex(),
      items: [
        FloatingIslandItem(
          icon: LucideIcons.home,
          onTap: () {
            if (!currentRoute.startsWith(AppRoutePath.dashboard) &&
                currentRoute != '/') {
              context.go(AppRoutePath.dashboard);
            }
          },
        ),
        FloatingIslandItem(
          icon: LucideIcons.history,
          onTap: () {
            // context.go(AppRoutePath.history);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('History - Coming Soon')),
            );
          },
        ),
        FloatingIslandItem(
          icon: LucideIcons.plus,
          isCenter: true,
          onTap: () {
            // context.go(AppRoutePath.addGig);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Add Gig - Coming Soon')),
            );
          },
        ),
        FloatingIslandItem(
          icon: LucideIcons.messageCircle,
          onTap: () {
            // TODO: Navigate to chat when route is ready
            // context.go(AppRoutePath.chat);
            ScaffoldMessenger.of(
              context,
            ).showSnackBar(const SnackBar(content: Text('Chat - Coming Soon')));
          },
        ),
        FloatingIslandItem(
          icon: LucideIcons.userCircle2,
          onTap: () {
            // TODO: Navigate to profile when route is ready
            // context.go(AppRoutePath.profile);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Profile - Coming Soon')),
            );
          },
        ),
      ],
    );
  }
}
