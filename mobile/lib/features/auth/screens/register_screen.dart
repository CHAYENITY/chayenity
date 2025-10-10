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
    return const CustomStatusBar(
      child: Scaffold(
        backgroundColor: AppColors.background,
        resizeToAvoidBottomInset: true,
        body: SafeArea(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 32),
            child: Center(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Header
                    Center(
                      child: AuthHeader(title: 'เพื่อนที่พร้อมช่วย รอคุณอยู่!'),
                    ),

                    SizedBox(height: 32),

                    // Register Form
                    _RegisterFormFields(),

                    SizedBox(height: 24),

                    // Register Button
                    _RegisterButton(),

                    SizedBox(height: 8),

                    // Google Sign In Button
                    _GoogleRegisterButton(),

                    SizedBox(height: 32),

                    // Navigation to Login
                    _NavigationToLogin(),
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

// Register Form Fields Widget (rebuilds only when form state changes)
class _RegisterFormFields extends ConsumerWidget {
  const _RegisterFormFields();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(registerFormProvider);
    final isLoading = ref.watch(isLoadingProvider('auth-register'));
    final isGoogleLoading = ref.watch(isLoadingProvider('auth-google'));
    final isDisabled = isLoading || isGoogleLoading;

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
        _PasswordField(isDisabled: isDisabled),

        const SizedBox(height: 24),

        // Confirm Password Field
        _ConfirmPasswordField(isDisabled: isDisabled),

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

// Password Field Widget (rebuilds only when password or obscure state changes)
class _PasswordField extends ConsumerWidget {
  final bool isDisabled;

  const _PasswordField({required this.isDisabled});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final password = ref.watch(
      registerFormProvider.select((state) => state.password),
    );
    final obscurePassword = ref.watch(
      registerFormProvider.select((state) => state.obscurePassword),
    );

    return AuthTextField(
      label: 'รหัสผ่าน',
      hintText: '••••••••••••••',
      obscureText: obscurePassword,
      value: password,
      onChanged: (value) =>
          ref.read(registerFormProvider.notifier).setPassword(value),
      isDisabled: isDisabled,
      suffixIcon: IconButton(
        icon: Icon(
          obscurePassword ? Icons.visibility_off : Icons.visibility,
          color: AppColors.primary,
        ),
        onPressed: isDisabled
            ? null
            : () => ref
                  .read(registerFormProvider.notifier)
                  .togglePasswordVisibility(),
      ),
    );
  }
}

// Confirm Password Field Widget (rebuilds only when confirm password or obscure state changes)
class _ConfirmPasswordField extends ConsumerWidget {
  final bool isDisabled;

  const _ConfirmPasswordField({required this.isDisabled});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final confirmPassword = ref.watch(
      registerFormProvider.select((state) => state.confirmPassword),
    );
    final obscureConfirmPassword = ref.watch(
      registerFormProvider.select((state) => state.obscureConfirmPassword),
    );

    return AuthTextField(
      label: 'ยืนยันรหัสผ่าน',
      hintText: '••••••••••••••',
      obscureText: obscureConfirmPassword,
      value: confirmPassword,
      onChanged: (value) =>
          ref.read(registerFormProvider.notifier).setConfirmPassword(value),
      isDisabled: isDisabled,
      suffixIcon: IconButton(
        icon: Icon(
          obscureConfirmPassword ? Icons.visibility_off : Icons.visibility,
          color: AppColors.primary,
        ),
        onPressed: isDisabled
            ? null
            : () => ref
                  .read(registerFormProvider.notifier)
                  .toggleConfirmPasswordVisibility(),
      ),
    );
  }
}

// Register Button Widget (rebuilds only when isValid or isLoading changes)
class _RegisterButton extends ConsumerWidget {
  const _RegisterButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      registerFormProvider.select((state) => state.isValid),
    );
    final isLoading = ref.watch(isLoadingProvider('auth-register'));

    return PrimaryButton(
      text: 'สร้างบัญชี Hourz',
      onPressed: isValid
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
      isDisabled: !isValid,
    );
  }
}

// Google Register Button Widget (rebuilds only when loading states change)
class _GoogleRegisterButton extends ConsumerWidget {
  const _GoogleRegisterButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isGoogleLoading = ref.watch(isLoadingProvider('auth-google'));
    final isRegisterLoading = ref.watch(isLoadingProvider('auth-register'));

    return GoogleSignInButton(
      text: 'ลงทะเบียนด้วย Google',
      onPressed: () => ref.read(authProvider.notifier).loginWithGoogle(),
      isLoading: isGoogleLoading,
      isDisabled: isRegisterLoading,
    );
  }
}

// Navigation to Login Widget (static, never rebuilds)
class _NavigationToLogin extends StatelessWidget {
  const _NavigationToLogin();

  @override
  Widget build(BuildContext context) {
    return AuthNavigationLink(
      question: 'มีบัญชีแล้ว?',
      linkText: 'เข้าสู่ระบบเลย',
      onTap: () => context.goNamed('login'),
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
