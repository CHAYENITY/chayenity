import 'dart:math' as math;
import 'package:flutter/material.dart';

import 'package:community_marketplace/features/presentation/screens/terms_screen.dart';
import 'package:community_marketplace/features/presentation/screens/onboarding_screen.dart';
import 'package:community_marketplace/features/auth/screens/sign_in_screen.dart';
import 'package:community_marketplace/features/dashboard/screens/dashboard_screen.dart';

class SplashScreen extends StatefulWidget {
  final bool isFreshInstall;

  const SplashScreen({super.key, this.isFreshInstall = true});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}


class _SplashScreenState extends State<SplashScreen> {
  bool termsAccepted = false; // จำลองว่ายังไม่ยืนยัน terms
  bool onboardingSeen = false; // จำลองว่ายังไม่เคยเปิดหน้า onboarding
  bool isSignedIn = false; // จำลองว่ายังไม่ได้ SignIn

  @override
  void initState() {
    super.initState();
    _checkAndNavigate();
  }

  void _checkAndNavigate() async {
    await Future.delayed(const Duration(seconds: 3));

    if (!mounted) return;

    if (widget.isFreshInstall) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const TermsScreen()),
      );
    } else {
      if (!termsAccepted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const TermsScreen()),
        );
      } else if (!onboardingSeen) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const OnboardingScreen()),
        );
      } else if (!isSignedIn) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const SignInScreen()),
        );
      } else {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const DashboardScreen()),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isPortrait = size.height > size.width;

    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          // * Background
          Padding(
            padding: const EdgeInsets.only(top: 70.0, right: 70.0),
            child: Transform.rotate(
              angle: isPortrait ? math.pi / 2 : 0,
              child: FittedBox(
                fit: BoxFit.cover,
                child: Image.asset(
                  'assets/bg/community-marketplace-logo-bg-16-9.png',
                ),
              ),
            ),
          ),

          // * Logo
          Center(
            child: LayoutBuilder(
              builder: (context, constraints) {
                double logoWidth = constraints.maxWidth * 0.4;
                return Image.asset(
                  'assets/logo/community-marketplace-logo.png',
                  width: logoWidth,
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
