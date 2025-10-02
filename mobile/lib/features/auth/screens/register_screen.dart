import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';

import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/custom_status_bar.dart';

import '../providers/auth_provider.dart';
import '../widgets/auth_widgets.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(registerFormProvider);
    final isLoading = ref.watch(isLoadingProvider('auth-register'));
    final isGoogleLoading = ref.watch(isLoadingProvider('auth-google'));

    return CustomStatusBar(
      child: Scaffold(
        backgroundColor: AppColors.background,
        resizeToAvoidBottomInset: true,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Center(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Header
                    const Center(
                      child: AuthHeader(title: 'เพื่อนที่พร้อมช่วย รอคุณอยู่!'),
                    ),

                    const SizedBox(height: 32),

                    // Register Form
                    _RegisterForm(
                      formState: formState,
                      isDisabled: isLoading || isGoogleLoading,
                    ),

                    const SizedBox(height: 24),

                    // Register Button
                    PrimaryButton(
                      text: 'สร้างบัญชี Hourz',
                      onPressed: formState.isValid
                          ? () async {
                              final success = await ref
                                  .read(registerFormProvider.notifier)
                                  .submit();
                              if (success && context.mounted) {
                                context.go(AppRoutePath.login);
                              }
                            }
                          : null,
                      isLoading: isLoading,
                      isDisabled: !formState.isValid,
                    ),

                    const SizedBox(height: 8),

                    // Google Sign In Button
                    GoogleSignInButton(
                      text: 'ลงทะเบียนด้วย Google',
                      onPressed: () =>
                          ref.read(authProvider.notifier).loginWithGoogle(),
                      isLoading: isGoogleLoading,
                      isDisabled: isLoading,
                    ),

                    const SizedBox(height: 32),

                    // Navigation to Login
                    AuthNavigationLink(
                      question: 'มีบัญชีแล้ว?',
                      linkText: 'เข้าสู่ระบบเลย',
                      onTap: () => context.goNamed('login'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// Private Register Form Widget
class _RegisterForm extends ConsumerWidget {
  final RegisterFormState formState;
  final bool isDisabled;

  const _RegisterForm({required this.formState, this.isDisabled = false});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        // Email Field
        AuthTextField(
          label: 'อีเมล',
          hintText: 'user@chavenity.com',
          keyboardType: TextInputType.emailAddress,
          value: formState.email,
          onChanged: (value) =>
              ref.read(registerFormProvider.notifier).setEmail(value),
          isDisabled: isDisabled,
        ),

        const SizedBox(height: 24),

        // Password Field
        AuthTextField(
          label: 'รหัสผ่าน',
          hintText: '••••••••••••••',
          obscureText: formState.obscurePassword,
          value: formState.password,
          onChanged: (value) =>
              ref.read(registerFormProvider.notifier).setPassword(value),
          isDisabled: isDisabled,
          suffixIcon: IconButton(
            icon: Icon(
              formState.obscurePassword
                  ? Icons.visibility_off
                  : Icons.visibility,
              color: AppColors.primary,
            ),
            onPressed: isDisabled
                ? null
                : () => ref
                      .read(registerFormProvider.notifier)
                      .togglePasswordVisibility(),
          ),
        ),

        const SizedBox(height: 24),

        // Confirm Password Field
        AuthTextField(
          label: 'ยืนยันรหัสผ่าน',
          hintText: '••••••••••••••',
          obscureText: formState.obscureConfirmPassword,
          value: formState.confirmPassword,
          onChanged: (value) =>
              ref.read(registerFormProvider.notifier).setConfirmPassword(value),
          isDisabled: isDisabled,
          suffixIcon: IconButton(
            icon: Icon(
              formState.obscureConfirmPassword
                  ? Icons.visibility_off
                  : Icons.visibility,
              color: AppColors.primary,
            ),
            onPressed: isDisabled
                ? null
                : () => ref
                      .read(registerFormProvider.notifier)
                      .toggleConfirmPasswordVisibility(),
          ),
        ),

        const SizedBox(height: 24),

        // Password Match Validation
        if (formState.confirmPassword.isNotEmpty &&
            !formState.isPasswordMatch) ...[
          _PasswordMismatchWarning(),
          const SizedBox(height: 16),
        ],

        // Terms Checkbox
        TermsCheckbox(
          value: formState.agreeToTerms,
          onChanged: (value) => ref
              .read(registerFormProvider.notifier)
              .setAgreeToTerms(value ?? false),
          isDisabled: isDisabled,
        ),
      ],
    );
  }
}

// Private Password Mismatch Warning Widget
class _PasswordMismatchWarning extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(25),
        border: Border.all(color: AppColors.destructive),
      ),
      child: Row(
        children: [
          Icon(
            Icons.warning_amber_rounded,
            size: 16,
            color: AppColors.destructive,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'รหัสผ่านไม่ตรงกัน',
              style: TextStyle(fontSize: 12, color: AppColors.destructive),
            ),
          ),
        ],
      ),
    );
  }
}
