import 'package:flutter/material.dart';
import 'package:hourz/shared/providers/index.dart';

class AppTypography {
  static const String fontFamily = 'IBM_Plex_Sans_Thai';

  static TextTheme get textTheme => const TextTheme(
    displayLarge: displayLarge,
    headlineMedium: headlineMedium,
    headlineSmall: headlineSmall,
    titleMedium: titleMedium,
    bodyMedium: bodyMedium,
    bodySmall: bodySmall,
    labelSmall: labelSmall,
  );

  // --- Display / Headline ---
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w500, // Bold
    color: AppColors.foreground, // * หัวข้อหลัก
    height: 1.5,
    letterSpacing: 0,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    fontWeight: FontWeight.w500, // SemiBold
    color: AppColors.foreground, // * หัวข้อรอง
    letterSpacing: 0,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w500, // Medium
    color: AppColors.foreground,
    letterSpacing: 0,
  );

  // Theme.of(context).textTheme.titleMedium
  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600, // Medium
    color: AppColors.foreground,
    letterSpacing: 0,
  );

  // --- Body / Paragraph ---
  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500, // Regular
    color: AppColors.foreground,
    letterSpacing: 0,
  );

  // Theme.of(context).textTheme.bodySmall
  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: AppColors.foreground, // ข้อความรอง
    letterSpacing: 0,
  );

  // --- Caption / Label ---
  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 10,
    fontWeight: FontWeight.w600, // Light
    color: AppColors.foreground,
    letterSpacing: 0,
  );
}
