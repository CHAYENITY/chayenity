import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class CustomStatusBar extends StatelessWidget {
  final Widget child;
  final Color? statusBarColor;

  const CustomStatusBar({required this.child, this.statusBarColor, super.key});

  @override
  Widget build(BuildContext context) {
    final brightness = Theme.of(context).brightness;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: statusBarColor ?? Colors.transparent,
        statusBarIconBrightness: brightness == Brightness.light
            ? Brightness.light
            : Brightness.dark, // Android
        statusBarBrightness: brightness == Brightness.light
            ? Brightness.light
            : Brightness.dark, // iOS
      ),
      child: child,
    );
  }
}
