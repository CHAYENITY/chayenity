import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/custom_status_bar.dart';
import '../providers/auth_provider.dart';
import '../widgets/auth_widgets.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(loginFormProvider);
    final isLoading = ref.watch(isLoadingProvider('auth-login'));
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
                      child: AuthHeader(title: 'ยินดีต้อนรับกลับมา!'),
                    ),

                    const SizedBox(height: 32),

                    // Login Form
                    _LoginForm(
                      formState: formState,
                      isDisabled: isLoading || isGoogleLoading,
                    ),

                    const SizedBox(height: 24),

                    // Login Button
                    PrimaryButton(
                      text: 'เข้าสู่ระบบ',
                      onPressed: formState.isValid
                          ? () => ref.read(loginFormProvider.notifier).submit()
                          : null,
                      isLoading: isLoading,
                      isDisabled: !formState.isValid,
                    ),

                    const SizedBox(height: 8),

                    // Google Sign In Button
                    GoogleSignInButton(
                      text: 'เข้าสู่ระบบด้วย Google',
                      onPressed: () =>
                          ref.read(authProvider.notifier).loginWithGoogle(),
                      isLoading: isGoogleLoading,
                      isDisabled: isLoading,
                    ),

                    const SizedBox(height: 32),

                    // Navigation to Register
                    AuthNavigationLink(
                      question: 'ยังไม่มีบัญชี?',
                      linkText: 'มาลงทะเบียนเลย',
                      onTap: () => context.goNamed('register'),
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

// Private Login Form Widget
class _LoginForm extends ConsumerWidget {
  final LoginFormState formState;
  final bool isDisabled;

  const _LoginForm({required this.formState, this.isDisabled = false});

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
              ref.read(loginFormProvider.notifier).setEmail(value),
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
              ref.read(loginFormProvider.notifier).setPassword(value),
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
                      .read(loginFormProvider.notifier)
                      .togglePasswordVisibility(),
          ),
        ),
      ],
    );
  }
}
