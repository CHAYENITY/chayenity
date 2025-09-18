import 'package:flutter/material.dart';

class AppTypography {
  static const String fontFamily = 'Prompt';

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
    color: Colors.black, // * หัวข้อหลัก
    height: 1.5,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    fontWeight: FontWeight.w500, // SemiBold
    color: Colors.black87, // * หัวข้อรอง
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w500, // Medium
    color: Colors.black87,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500, // Medium
    color: Colors.black87,
  );

  // --- Body / Paragraph ---
  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400, // Regular
    color: Colors.black87,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: Colors.black87, // ข้อความรอง
  );

  // --- Caption / Label ---
  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w300, // Light
    color: Colors.black87,
  );
}
