import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:hourz/shared/constants/app_routes.dart';
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
                    Center(child: AuthHeader(title: 'ยินดีต้อนรับกลับมา!')),

                    SizedBox(height: 32),

                    // Login Form
                    _LoginFormFields(),

                    SizedBox(height: 24),

                    // Login Button
                    _LoginButton(),

                    SizedBox(height: 8),

                    // Google Sign In Button
                    _GoogleLoginButton(),

                    SizedBox(height: 32),

                    // Navigation to Register
                    _NavigationToRegister(),
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

// Login Form Fields Widget (rebuilds only when form state changes)
class _LoginFormFields extends ConsumerWidget {
  const _LoginFormFields();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final email = ref.watch(loginFormProvider.select((state) => state.email));
    final isLoading = ref.watch(isLoadingProvider('auth-login'));
    final isGoogleLoading = ref.watch(isLoadingProvider('auth-google'));
    final isDisabled = isLoading || isGoogleLoading;

    return Column(
      children: [
        // Email Field
        AuthTextField(
          label: 'อีเมล',
          hintText: 'user@chavenity.com',
          keyboardType: TextInputType.emailAddress,
          value: email,
          onChanged: (value) =>
              ref.read(loginFormProvider.notifier).setEmail(value),
          isDisabled: isDisabled,
        ),

        const SizedBox(height: 24),

        // Password Field
        _PasswordField(isDisabled: isDisabled),
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
      loginFormProvider.select((state) => state.password),
    );
    final obscurePassword = ref.watch(
      loginFormProvider.select((state) => state.obscurePassword),
    );

    return AuthTextField(
      label: 'รหัสผ่าน',
      hintText: '••••••••••••••',
      obscureText: obscurePassword,
      value: password,
      onChanged: (value) =>
          ref.read(loginFormProvider.notifier).setPassword(value),
      isDisabled: isDisabled,
      suffixIcon: IconButton(
        icon: Icon(
          obscurePassword ? Icons.visibility_off : Icons.visibility,
          color: AppColors.primary,
        ),
        onPressed: isDisabled
            ? null
            : () => ref
                  .read(loginFormProvider.notifier)
                  .togglePasswordVisibility(),
      ),
    );
  }
}

// Login Button Widget (rebuilds only when isValid or isLoading changes)
class _LoginButton extends ConsumerWidget {
  const _LoginButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      loginFormProvider.select((state) => state.isValid),
    );
    final isLoading = ref.watch(isLoadingProvider('auth-login'));

    return PrimaryButton(
      text: 'เข้าสู่ระบบ',
      onPressed: isValid
          ? () async {
              final isProfileSetup = await ref
                  .read(loginFormProvider.notifier)
                  .submit();
              if (context.mounted) {
                if (isProfileSetup) {
                  context.go(AppRoutePath.dashboard);
                } else {
                  context.go(AppRoutePath.profileSetup);
                }
              }
            }
          : null,
      isLoading: isLoading,
      isDisabled: !isValid,
    );
  }
}

// Google Login Button Widget (rebuilds only when loading states change)
class _GoogleLoginButton extends ConsumerWidget {
  const _GoogleLoginButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isGoogleLoading = ref.watch(isLoadingProvider('auth-google'));
    final isLoginLoading = ref.watch(isLoadingProvider('auth-login'));

    return GoogleSignInButton(
      text: 'เข้าสู่ระบบด้วย Google',
      onPressed: () => ref.read(authProvider.notifier).loginWithGoogle(),
      isLoading: isGoogleLoading,
      isDisabled: isLoginLoading,
    );
  }
}

// Navigation to Register Widget (static, never rebuilds)
class _NavigationToRegister extends StatelessWidget {
  const _NavigationToRegister();

  @override
  Widget build(BuildContext context) {
    return AuthNavigationLink(
      question: 'ยังไม่มีบัญชี?',
      linkText: 'มาลงทะเบียนเลย',
      onTap: () => context.goNamed('register'),
    );
  }
}
