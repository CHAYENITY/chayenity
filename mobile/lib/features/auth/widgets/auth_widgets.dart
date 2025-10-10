import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/gestures.dart';

import 'package:hourz/shared/constants/assets.dart';
import 'package:hourz/shared/providers/index.dart';

import 'terms_dialog.dart';

// Auth Header Widget
class AuthHeader extends StatelessWidget {
  final String title;
  final String? subtitle;

  const AuthHeader({super.key, required this.title, this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w600),
        ),
        if (subtitle != null) ...[
          const SizedBox(height: 8),
          Text(
            subtitle!,
            style: TextStyle(fontSize: 14, color: AppColors.mutedForeground),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}

// Custom Text Field Widget
class AuthTextField extends ConsumerWidget {
  final String label;
  final String hintText;
  final bool obscureText;
  final TextInputType keyboardType;
  final void Function(String) onChanged;
  final String? value;
  final Widget? suffixIcon;
  final bool isDisabled;

  const AuthTextField({
    super.key,
    required this.label,
    required this.hintText,
    required this.onChanged,
    this.obscureText = false,
    this.keyboardType = TextInputType.text,
    this.value,
    this.suffixIcon,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        TextFormField(
          enabled: !isDisabled,
          initialValue: value,
          obscureText: obscureText,
          keyboardType: keyboardType,
          onChanged: onChanged,
          decoration: InputDecoration(
            hintText: hintText,
            suffixIcon: suffixIcon,
          ),
        ),
      ],
    );
  }
}

// Primary Button Widget
class PrimaryButton extends ConsumerWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isDisabled;

  const PrimaryButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: (isDisabled || isLoading) ? null : onPressed,
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 12),
          elevation: 0,
        ),
        child: isLoading
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppColors.primaryForeground,
                  ),
                ),
              )
            : Text(text, style: const TextStyle(fontWeight: FontWeight.w600)),
      ),
    );
  }
}

// Google Sign In Button Widget
class GoogleSignInButton extends ConsumerWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isDisabled;

  const GoogleSignInButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        onPressed: (isDisabled || isLoading) ? null : onPressed,
        style: OutlinedButton.styleFrom(padding: const EdgeInsets.all(6)),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 32,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.grey),
                      ),
                    )
                  : Image.asset(
                      Assets.googleLogo,
                      height: 32,
                      width: 32,
                      errorBuilder: (context, error, stackTrace) => const Icon(
                        Icons.g_mobiledata,
                        size: 24,
                        color: Colors.red,
                      ),
                    ),
            ),
            Center(
              child: Text(
                text,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: AppColors.foreground,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Terms and Conditions Checkbox Widget
class TermsCheckbox extends ConsumerWidget {
  final bool value;
  final void Function(bool?) onChanged;
  final bool isDisabled;

  const TermsCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Transform.translate(
          offset: const Offset(-6, 0),
          child: Checkbox(
            value: value,
            onChanged: isDisabled
                ? null
                : (bool? newValue) => _handleCheckboxTap(context, newValue),
            activeColor: AppColors.background,
            checkColor: AppColors.mutedForeground,
            side: WidgetStateBorderSide.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return const BorderSide(color: AppColors.muted);
              } else {
                return const BorderSide(color: AppColors.muted);
              }
            }),
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            visualDensity: VisualDensity.compact,
          ),
        ),
        Expanded(
          child: GestureDetector(
            onTap: isDisabled
                ? null
                : () => _handleCheckboxTap(context, !value),
            child: Padding(
              padding: const EdgeInsets.only(top: 5),
              child: RichText(
                text: TextSpan(
                  style: AppTheme.richText,
                  children: [
                    const TextSpan(text: 'ฉันได้อ่านและยอมรับ '),
                    TextSpan(
                      text: 'ข้อกำหนดและเงื่อนไข',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.primary,
                        decoration: TextDecoration.underline,
                      ),
                      recognizer: TapGestureRecognizer()
                        ..onTap = () => _showTermsDialog(context),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  void _handleCheckboxTap(BuildContext context, bool? newValue) {
    if (newValue == true) {
      // Show terms dialog when trying to check the checkbox
      _showTermsDialog(context);
    } else {
      // Allow unchecking directly
      onChanged(false);
    }
  }

  void _showTermsDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return TermsDialog(
          onAccept: () {
            Navigator.of(context).pop();
            onChanged(true);
          },
          onCancel: () {
            Navigator.of(context).pop();
            onChanged(false);
          },
        );
      },
    );
  }
}

// Navigation Link Widget
class AuthNavigationLink extends StatelessWidget {
  final String question;
  final String linkText;
  final VoidCallback onTap;

  const AuthNavigationLink({
    super.key,
    required this.question,
    required this.linkText,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: RichText(
        text: TextSpan(
          style: AppTheme.richText,
          children: [
            TextSpan(text: '$question '),
            TextSpan(
              text: linkText,
              style: TextStyle(
                color: AppColors.primary,
                decoration: TextDecoration.underline,
              ),
              recognizer: TapGestureRecognizer()..onTap = onTap,
            ),
          ],
        ),
      ),
    );
  }
}
