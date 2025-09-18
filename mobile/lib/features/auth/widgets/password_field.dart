import 'package:flutter/material.dart';

class PasswordField extends StatelessWidget {
  final TextEditingController controller;
  final String labelText;
  final String? hintText;
  final bool isPasswordVisible;
  final VoidCallback onVisibilityToggle;
  final Function(String)? onChanged;
  final String? Function(String?)? validator;
  final bool enabled;

  const PasswordField({
    super.key,
    required this.controller,
    required this.labelText,
    required this.hintText,
    required this.isPasswordVisible,
    required this.onVisibilityToggle,
    this.onChanged,
    this.validator,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: !isPasswordVisible,
      enabled: enabled,
      onChanged: onChanged,
      validator: validator,
      style: const TextStyle(fontSize: 16, color: Colors.black),
      decoration: InputDecoration(
        labelText: labelText,
        hintText: hintText,
        hintStyle: const TextStyle(color: Colors.grey, fontSize: 16),
        border: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.grey),
        ),
        enabledBorder: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.grey),
        ),
        focusedBorder: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.black, width: 2),
        ),
        errorBorder: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.red),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 0, vertical: 16),
        suffixIcon: IconButton(
          icon: AnimatedSwitcher(
            duration: const Duration(milliseconds: 200),
            child: Transform.scale(
              scaleX: isPasswordVisible ? 1.0 : -1.0,
              child: Icon(
                isPasswordVisible
                    ? Icons.visibility
                    : Icons.visibility_off_outlined,
                key: ValueKey(isPasswordVisible),
                color: isPasswordVisible
                    ? Colors.blue.shade600
                    : Colors.grey.shade600,
                size: 22,
              ),
            ),
          ),
          onPressed: onVisibilityToggle,
          splashRadius: 20,
          tooltip: isPasswordVisible ? 'ซ่อนรหัสผ่าน' : 'แสดงรหัสผ่าน',
        ),
      ),
    );
  }
}
