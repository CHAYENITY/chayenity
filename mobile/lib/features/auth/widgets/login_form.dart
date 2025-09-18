import 'package:chayenity/main.dart';
import 'package:chayenity/shared/theme/color_schemas.dart';

import '../widgets/password_field.dart';

import 'package:flutter/material.dart';

class LoginForm extends StatelessWidget {
  const LoginForm({super.key});

  const LoginForm({super.key, required this.provider});

  void _handleForgotPassword(
    BuildContext context,
    LoginProvider provider,
  ) async {
    if (!provider.isEmailValid) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Center(child: Text('กรุณากรอกอีเมลที่ถูกต้องก่อน')),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    try {
      await provider.sendPasswordReset();

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(
              child: Text('ส่งลิงก์รีเซ็ตรหัสผ่านไปยังอีเมลของคุณแล้ว'),
            ),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(child: Text(error.toString())),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  void _handleEmailLogin(BuildContext context, LoginProvider provider) async {
    try {
      await provider.loingWithEmail();

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(child: Text('เข้าสู่ระบบสำเร็จ!')),
            backgroundColor: AppColors.success,
          ),
        );

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const MainApp()),
        );
      }
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(error.toString()),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  void _handleEmailCheck(BuildContext context, LoginProvider provider) async {
    try {
      final emailExists = await provider.checkEmailExists();

      if (context.mounted) {
        if (!emailExists) {
          // Email doesn't exist, navigate to register
          final result = await Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) =>
                  SignUpScreen(email: provider.emailController.text.trim()),
            ),
          );

          if (context.mounted) {
            // If register was successful, reset the form for Login
            if (result == true) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Center(
                    child: Text('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ'),
                  ),
                  backgroundColor: AppColors.success,
                ),
              );
            }
          }
        }
      }
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(child: Text('เกิดข้อผิดพลาด: ${error.toString()}')),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: provider.formKey,
      child: Selector<LoginProvider, bool>(
        selector: (_, p) => p.showPasswordField,
        builder: (context, showPasswordField, child) {
          return Column(
            children: [
              _buildEmailField(provider),
              const SizedBox(height: 24),
              if (showPasswordField) ...[
                _buildPasswordField(provider),
                const SizedBox(height: 16),
              ],
              SizedBox(height: showPasswordField ? 16 : 32),
              _buildActionButton(context, provider),
              const SizedBox(height: 16),
              _buildRegisterAndForgotPassword(context, provider),
            ],
          );
        },
      ),
    );
  }

  Widget _buildEmailField(LoginProvider provider) {
    return TextFormField(
      controller: provider.emailController,
      keyboardType: TextInputType.emailAddress,
      style: const TextStyle(fontSize: 16, color: Colors.black),
      decoration: InputDecoration(
        labelText: 'อีเมล',
        hintText: 'กรอกอีเมลของคุณ',
        hintStyle: TextStyle(color: Colors.grey, fontSize: 16),
        border: UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.grey),
        ),
        enabledBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.grey),
        ),
        focusedBorder: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.black, width: 2),
        ),
        errorBorder: const UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.red),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 0, vertical: 16),
      ),
      onChanged: provider.onEmailChanged,
      validator: provider.validateEmail,
    );
  }

  Widget _buildPasswordField(LoginProvider provider) {
    return Selector<LoginProvider, bool>(
      selector: (_, p) => p.isPasswordVisible,
      builder: (context, isPasswordVisible, child) {
        return PasswordField(
          controller: provider.passwordController,
          labelText: "รหัสผ่าน",
          hintText: 'กรอกรหัสผ่านของคุณ',
          isPasswordVisible: isPasswordVisible,
          onVisibilityToggle: provider.togglePasswordVisibility,
          onChanged: provider.onPasswordChanged,
          validator: provider.validatePassword,
        );
      },
    );
  }

  Widget _buildActionButton(BuildContext context, LoginProvider provider) {
    return Selector<
      LoginProvider,
      ({
        bool canCheckEmail,
        bool isLoading,
        bool emailChecked,
        bool showPasswordField,
        bool canLogin,
      })
    >(
      selector: (_, p) => (
        canCheckEmail: p.canCheckEmail,
        isLoading: p.isLoading,
        emailChecked: p.emailChecked,
        showPasswordField: p.showPasswordField,
        canLogin: p.canLogin,
      ),
      builder: (context, state, child) {
        if (!state.emailChecked) {
          return Button(
            text: state.isLoading ? 'กำลังตรวจสอบ...' : 'เข้าใช้งานด้วยอีเมล',
            onPressed: state.canCheckEmail
                ? () => _handleEmailCheck(context, provider)
                : () {},
            isEnabled: state.canCheckEmail,
          );
        } else if (state.showPasswordField) {
          return ConfirmButton(
            text: state.isLoading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ',
            onPressed: state.canLogin
                ? () => _handleEmailLogin(context, provider)
                : () {},
            isEnabled: state.canLogin,
          );
        }
        return const SizedBox.shrink();
      },
    );
  }

  Widget _buildRegisterAndForgotPassword(
    BuildContext context,
    LoginProvider provider,
  ) {
    if (!provider.emailChecked) return const SizedBox.shrink();
    return Center(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          if (provider.showPasswordField)
            TextButton(
              onPressed: () {
                provider.resetForm();
              },
              child: const Text(
                'กรอกอีเมลใหม่',
                style: TextStyle(color: Colors.blue, fontSize: 14),
              ),
            ),
          const SizedBox(height: 20),
          TextButton(
            onPressed: () => _handleForgotPassword(context, provider),
            child: const Text(
              'ลืมรหัสผ่าน?',
              style: TextStyle(color: Colors.blue, fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }
}
