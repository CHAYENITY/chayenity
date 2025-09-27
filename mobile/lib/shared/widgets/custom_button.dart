import 'package:flutter/material.dart';

enum ButtonVariant { primary, secondary, outline, text }

enum ButtonSize { small, medium, large }

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final ButtonVariant variant;
  final ButtonSize size;
  final bool isLoading;
  final Widget? icon;
  final bool isFullWidth;

  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.isFullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEnabled = onPressed != null && !isLoading;

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: _getHeight(),
      child: _buildButton(context, theme, isEnabled),
    );
  }

  Widget _buildButton(BuildContext context, ThemeData theme, bool isEnabled) {
    switch (variant) {
      case ButtonVariant.primary:
        return ElevatedButton(
          onPressed: isEnabled ? onPressed : null,
          style: _getElevatedButtonStyle(theme),
          child: _buildButtonContent(theme.colorScheme.onPrimary),
        );
      case ButtonVariant.secondary:
        return ElevatedButton(
          onPressed: isEnabled ? onPressed : null,
          style: _getSecondaryButtonStyle(theme),
          child: _buildButtonContent(theme.colorScheme.onSecondary),
        );
      case ButtonVariant.outline:
        return OutlinedButton(
          onPressed: isEnabled ? onPressed : null,
          style: _getOutlinedButtonStyle(theme),
          child: _buildButtonContent(theme.colorScheme.primary),
        );
      case ButtonVariant.text:
        return TextButton(
          onPressed: isEnabled ? onPressed : null,
          style: _getTextButtonStyle(theme),
          child: _buildButtonContent(theme.colorScheme.primary),
        );
    }
  }

  Widget _buildButtonContent(Color textColor) {
    if (isLoading) {
      return SizedBox(
        width: _getIconSize(),
        height: _getIconSize(),
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(textColor),
        ),
      );
    }

    final textWidget = Text(
      text,
      style: TextStyle(
        fontSize: _getFontSize(),
        fontWeight: FontWeight.w600,
        color: textColor,
      ),
    );

    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [icon!, const SizedBox(width: 8), textWidget],
      );
    }

    return textWidget;
  }

  ButtonStyle _getElevatedButtonStyle(ThemeData theme) {
    return ElevatedButton.styleFrom(
      backgroundColor: theme.colorScheme.primary,
      foregroundColor: theme.colorScheme.onPrimary,
      elevation: 2,
      shadowColor: theme.colorScheme.shadow.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: _getPadding(),
    );
  }

  ButtonStyle _getSecondaryButtonStyle(ThemeData theme) {
    return ElevatedButton.styleFrom(
      backgroundColor: theme.colorScheme.secondary,
      foregroundColor: theme.colorScheme.onSecondary,
      elevation: 1,
      shadowColor: theme.colorScheme.shadow.withOpacity(0.05),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: _getPadding(),
    );
  }

  ButtonStyle _getOutlinedButtonStyle(ThemeData theme) {
    return OutlinedButton.styleFrom(
      foregroundColor: theme.colorScheme.primary,
      side: BorderSide(color: theme.colorScheme.outline, width: 1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: _getPadding(),
    );
  }

  ButtonStyle _getTextButtonStyle(ThemeData theme) {
    return TextButton.styleFrom(
      foregroundColor: theme.colorScheme.primary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: _getPadding(),
    );
  }

  EdgeInsetsGeometry _getPadding() {
    switch (size) {
      case ButtonSize.small:
        return const EdgeInsets.symmetric(horizontal: 12, vertical: 8);
      case ButtonSize.medium:
        return const EdgeInsets.symmetric(horizontal: 16, vertical: 12);
      case ButtonSize.large:
        return const EdgeInsets.symmetric(horizontal: 24, vertical: 16);
    }
  }

  double _getHeight() {
    switch (size) {
      case ButtonSize.small:
        return 36;
      case ButtonSize.medium:
        return 48;
      case ButtonSize.large:
        return 56;
    }
  }

  double _getFontSize() {
    switch (size) {
      case ButtonSize.small:
        return 14;
      case ButtonSize.medium:
        return 16;
      case ButtonSize.large:
        return 18;
    }
  }

  double _getIconSize() {
    switch (size) {
      case ButtonSize.small:
        return 16;
      case ButtonSize.medium:
        return 20;
      case ButtonSize.large:
        return 24;
    }
  }
}
