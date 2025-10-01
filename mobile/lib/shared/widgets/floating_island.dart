import 'package:flutter/material.dart';
import 'package:hourz/shared/providers/index.dart';

class FloatingIsland extends StatelessWidget {
  final List<FloatingIslandItem> items;
  final int currentIndex;
  final double bottomPadding;
  final double horizontalPadding;
  final Color? backgroundColor;
  final Color? activeColor;
  final Color? inactiveColor;
  final double elevation;
  final BorderRadius? borderRadius;

  const FloatingIsland({
    super.key,
    required this.items,
    this.currentIndex = 0,
    this.bottomPadding = 32.0,
    this.horizontalPadding = 44.0,
    this.backgroundColor,
    this.activeColor,
    this.inactiveColor,
    this.elevation = 8.0,
    this.borderRadius,
  }) : assert(
         items.length >= 2 && items.length <= 5,
         'Items must be between 2-5',
       );

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final bgColor =
        backgroundColor ??
        (isDark ? AppColors.background : AppColors.darkBackground);
    final activeItemColor = activeColor ?? AppColors.darkBackground;
    final activeItemBgColor = AppColors.secondary;
    final inactiveItemColor =
        inactiveColor ??
        (isDark ? AppColors.foreground : AppColors.darkForeground);
    final inactiveItemBgColor = Colors.transparent;

    return Positioned(
      left: horizontalPadding,
      right: horizontalPadding,
      bottom: bottomPadding,
      child: Material(
        elevation: elevation,
        borderRadius: borderRadius ?? BorderRadius.circular(32),
        color: bgColor,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(items.length, (index) {
              final item = items[index];
              final isActive = currentIndex == index;
              final isCenterItem = item.isCenter;

              return Expanded(
                child: _FloatingIslandButton(
                  icon: item.icon,
                  label: item.label,
                  isActive: isActive,
                  isCenter: isCenterItem,
                  onTap: item.onTap,
                  activeColor: activeItemColor,
                  activeBgColor: activeItemBgColor,
                  inactiveColor: inactiveItemColor,
                  inactiveBgColor: inactiveItemBgColor,
                  showLabel: item.showLabel,
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

/// Item configuration for FloatingIsland
class FloatingIslandItem {
  final IconData icon;
  final String? label;
  final VoidCallback onTap;
  final bool isCenter;
  final bool showLabel;

  const FloatingIslandItem({
    required this.icon,
    required this.onTap,
    this.label,
    this.isCenter = false,
    this.showLabel = false,
  });
}

/// Internal button widget for FloatingIsland items
class _FloatingIslandButton extends StatelessWidget {
  final IconData icon;
  final String? label;
  final bool isActive;
  final bool isCenter;
  final VoidCallback onTap;
  final Color activeColor;
  final Color activeBgColor;
  final Color inactiveColor;
  final Color inactiveBgColor;
  final bool showLabel;

  const _FloatingIslandButton({
    required this.icon,
    required this.isActive,
    required this.isCenter,
    required this.onTap,
    required this.activeColor,
    required this.activeBgColor,
    required this.inactiveColor,
    required this.inactiveBgColor,
    this.label,
    this.showLabel = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = isActive ? activeColor : inactiveColor;

    // Center item with larger elevated button
    if (isCenter) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ClipOval(
            child: Material(
              color: AppColors.primary,
              elevation: 4,
              shape: const CircleBorder(),
              child: InkWell(
                onTap: onTap,
                customBorder: const CircleBorder(),
                child: Container(
                  width: 56,
                  height: 56,
                  alignment: Alignment.center,
                  child: Icon(
                    icon,
                    color: AppColors.primaryForeground,
                    size: 28,
                  ),
                ),
              ),
            ),
          ),
        ],
      );
    }

    // Regular item
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        ClipOval(
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onTap,
              customBorder: const CircleBorder(),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: isActive ? activeBgColor : inactiveBgColor,
                  shape: BoxShape.circle,
                ),
                alignment: Alignment.center,
                child: Icon(icon, color: color, size: 28),
              ),
            ),
          ),
        ),
        if (showLabel && label != null) ...[
          const SizedBox(height: 4),
          Text(
            label!,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ],
    );
  }
}
