import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../controllers/login_form_controller.dart';
import '../providers/auth_providers.dart';
import '../../../shared/widgets/custom_text_field.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../shared/widgets/loading_overlay.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailFocusNode = FocusNode();
  final _passwordFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    // Controllers will be updated directly in onChanged callbacks
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _emailFocusNode.dispose();
    _passwordFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final formState = ref.watch(loginFormControllerProvider);
    final authState = ref.watch(authProvider);
    final isLoading = authState.isLoading;

    // Listen to auth errors and show snackbar
    ref.listen<String?>(authErrorProvider, (previous, next) {
      if (next != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next),
            backgroundColor: theme.colorScheme.error,
            behavior: SnackBarBehavior.floating,
            action: SnackBarAction(
              label: 'ปิด',
              textColor: theme.colorScheme.onError,
              onPressed: () {
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
                ref.read(authProvider.notifier).clearError();
              },
            ),
          ),
        );
      }
    });

    return Scaffold(
      body: LoadingOverlay(
        isLoading: isLoading,
        message: 'กำลังเข้าสู่ระบบ...',
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 60),

                // Logo and Title
                _buildHeader(theme),

                const SizedBox(height: 48),

                // Login Form
                _buildLoginForm(formState),

                const SizedBox(height: 24),

                // Login Button
                _buildLoginButton(formState, isLoading),

                const SizedBox(height: 16),

                // Demo Credentials Info
                _buildDemoInfo(theme),

                const SizedBox(height: 32),

                // Footer Links
                _buildFooter(theme),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(ThemeData theme) {
    return Column(
      children: [
        // Logo placeholder
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Icon(
            Icons.storefront_rounded,
            size: 40,
            color: theme.colorScheme.primary,
          ),
        ),

        const SizedBox(height: 24),

        Text(
          'ยินดีต้อนรับ',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurface,
          ),
        ),

        const SizedBox(height: 8),

        Text(
          'เข้าสู่ระบบเพื่อเริ่มใช้งาน Chayenity',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: theme.colorScheme.onSurface.withOpacity(0.7),
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildLoginForm(LoginFormState formState) {
    return Column(
      children: [
        CustomTextField(
          label: 'อีเมล',
          hintText: 'กรุณากรอกอีเมลของคุณ',
          keyboardType: TextInputType.emailAddress,
          textInputAction: TextInputAction.next,
          controller: _emailController,
          focusNode: _emailFocusNode,
          errorText: formState.emailError,
          prefixIcon: const Icon(Icons.email_outlined),
          onChanged: (value) {
            ref.read(loginFormControllerProvider.notifier).updateEmail(value);
          },
        ),

        const SizedBox(height: 20),

        CustomTextField(
          label: 'รหัสผ่าน',
          hintText: 'กรุณากรอกรหัสผ่านของคุณ',
          obscureText: !formState.isPasswordVisible,
          textInputAction: TextInputAction.done,
          controller: _passwordController,
          focusNode: _passwordFocusNode,
          errorText: formState.passwordError,
          prefixIcon: const Icon(Icons.lock_outline),
          suffixIcon: IconButton(
            icon: Icon(
              formState.isPasswordVisible
                  ? Icons.visibility_off_outlined
                  : Icons.visibility_outlined,
            ),
            onPressed: () {
              ref
                  .read(loginFormControllerProvider.notifier)
                  .togglePasswordVisibility();
            },
          ),
          onChanged: (value) {
            ref
                .read(loginFormControllerProvider.notifier)
                .updatePassword(value);
          },
        ),
      ],
    );
  }

  Widget _buildLoginButton(LoginFormState formState, bool isLoading) {
    return CustomButton(
      text: 'เข้าสู่ระบบ',
      onPressed: formState.isFormValid && !isLoading
          ? () {
              // Dismiss keyboard
              FocusScope.of(context).unfocus();

              // Submit form
              ref.read(loginFormControllerProvider.notifier).submitForm();
            }
          : null,
      variant: ButtonVariant.primary,
      size: ButtonSize.large,
      isFullWidth: true,
      isLoading: isLoading,
    );
  }

  Widget _buildDemoInfo(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.info_outline,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                'ข้อมูลสำหรับทดสอบ',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'อีเมล: demo@chayenity.com\nรหัสผ่าน: password123',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.8),
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter(ThemeData theme) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'ยังไม่มีบัญชี? ',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.7),
              ),
            ),
            GestureDetector(
              onTap: () {
                // Navigate to register screen
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('หน้าสมัครสมาชิกยังไม่พร้อมใช้งาน'),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              child: Text(
                'สมัครสมาชิก',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),

        const SizedBox(height: 16),

        GestureDetector(
          onTap: () {
            // Navigate to forgot password screen
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('หน้าลืมรหัสผ่านยังไม่พร้อมใช้งาน'),
                behavior: SnackBarBehavior.floating,
              ),
            );
          },
          child: Text(
            'ลืมรหัสผ่าน?',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
