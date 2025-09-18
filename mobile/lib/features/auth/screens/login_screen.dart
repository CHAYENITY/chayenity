import 'package:flutter/material.dart';

import 'package:chayenity/main.dart';
import 'package:chayenity/shared/theme/color_schemas.dart';

import '../widgets/login_form.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return _LoginScreenContent;
  }
}

class _LoginScreenContent extends StatelessWidget {
  const _LoginScreenContent();

  void _handleSocialSignIn(BuildContext context, String method) async {
    try {
      // switch (method) {
      //   case 'google':
      //     await provider.signInWithGoogle();
      //     break;
      //   case 'facebook':
      //     await provider.signInWithFacebook();
      //     break;
      //   case 'apple':
      //     await provider.signInWithApple();
      //     break;
      // }

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(child: Text('เข้าสู่ระบบสำเร็จ!')),
            backgroundColor: AppColors.success,
          ),
        );

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const MainApp()),
        );
      }
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Center(child: Text('เกิดข้อผิดพลาด: ${error.toString()}')),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<LoginProvider>(context, listen: false);
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
              ),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: IntrinsicHeight(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 20),
                        _buildHeader(context),
                        const SizedBox(height: 40),
                        LoginForm(provider: provider),
                        const SizedBox(height: 20),
                        _buildDivider(),

                        //   // * GOOGLE
                        //   const SizedBox(height: 24),
                        //   _buildSocialButton(
                        //     icon: Icons.g_mobiledata,
                        //     text: 'เข้าใช้งานด้วย Google',
                        //     backgroundColor: Colors.white,
                        //     textColor: Colors.black87,
                        //     onPressed: () =>
                        //         _handleSocialSignIn(context, provider, 'google'),
                        //   ),

                        //   // * FACEBOOK
                        //   const SizedBox(height: 12),
                        //   _buildSocialButton(
                        //     icon: Icons.facebook,
                        //     text: 'เข้าใช้งานด้วย Facebook',
                        //     backgroundColor: const Color(0xFF1877F2),
                        //     textColor: Colors.white,
                        //     onPressed: () => _handleSocialSignIn(
                        //       context,
                        //       provider,
                        //       'facebook',
                        //     ),
                        //   ),

                        //   const SizedBox(height: 12),
                        //   _buildSocialButton(
                        //     icon: Icons.apple,
                        //     text: 'เข้าใช้งานด้วย Apple',
                        //     backgroundColor: Colors.black,
                        //     textColor: Colors.white,
                        //     onPressed: () =>
                        //         _handleSocialSignIn(context, provider, 'apple'),
                        //   ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

Widget _buildHeader(BuildContext context) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Community Marketplace',
        style: Theme.of(context).textTheme.displayLarge?.copyWith(
          color: AppColors.primary,
          fontWeight: FontWeight.bold,
        ),
      ),
      const SizedBox(height: 40),
      Text(
        'สมัครบัญชีใหม่ หรือเข้าสู่ระบบ',
        style: Theme.of(context).textTheme.displayLarge!.copyWith(
          fontSize: 32,
          fontWeight: FontWeight.bold,
        ),
      ),
    ],
  );
}

Widget _buildDivider() {
  return Row(
    children: [
      Expanded(child: Container(height: 1, color: Colors.grey[300])),
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 16),
        child: Text('หรือ', style: TextStyle(color: Colors.grey, fontSize: 14)),
      ),
      Expanded(child: Container(height: 1, color: Colors.grey[300])),
    ],
  );
}

Widget _buildSocialButton({
  required IconData icon,
  required String text,
  required Color backgroundColor,
  required Color textColor,
  required VoidCallback onPressed,
}) {
  return SizedBox(
    width: double.infinity,
    height: 50,
    child: ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor,
        foregroundColor: textColor,
        elevation: 0,
        side: backgroundColor == Colors.white
            ? BorderSide(color: Colors.grey[300]!, width: 1)
            : null,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              const SizedBox(width: 16),
              if (icon == Icons.g_mobiledata) ...[
                Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    image: DecorationImage(
                      image: NetworkImage(
                        'https://developers.google.com/identity/images/g-logo.png',
                      ),
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
              ] else ...[
                Icon(icon, size: 20, color: textColor),
              ],
            ],
          ),
          Text(
            text,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: textColor,
            ),
          ),
        ],
      ),
    ),
  );
}
