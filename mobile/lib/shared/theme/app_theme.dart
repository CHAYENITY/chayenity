import 'package:flutter/material.dart';

import './color_schemas.dart';
import './typography.dart';

class AppTheme {
  static TextStyle get richText => AppTypography.bodyMedium;

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    fontFamily: AppTypography.fontFamily,
    textTheme: AppTypography.textTheme,
    colorScheme: ColorScheme.light(
      primary: AppColors.primary,
      secondary: AppColors.secondary,
      surface: AppColors.surface,
    ),
    scaffoldBackgroundColor: AppColors.background,
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.background,
      foregroundColor: AppColors.foreground,
      elevation: 0,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.primaryForeground,
        textStyle: AppTypography.textTheme.bodyMedium,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        backgroundColor: AppColors.background,
        textStyle: AppTypography.textTheme.bodyMedium,
        side: const BorderSide(color: AppColors.muted, width: 1),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        textStyle: AppTypography.textTheme.bodyMedium,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      hintStyle: TextStyle(
        fontSize: 12,
        color: AppColors.mutedForeground,
        fontWeight: FontWeight.w500,
        fontFamily: AppTypography.fontFamily,
      ),
      border: const UnderlineInputBorder(
        borderSide: BorderSide(color: AppColors.mutedForeground),
      ),
      enabledBorder: const UnderlineInputBorder(
        borderSide: BorderSide(color: AppColors.mutedForeground),
      ),
      focusedBorder: const UnderlineInputBorder(
        borderSide: BorderSide(color: AppColors.mutedForeground, width: 2),
      ),
      contentPadding: EdgeInsets.symmetric(vertical: 16),
    ),
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: AppTypography.fontFamily,
  );
}
