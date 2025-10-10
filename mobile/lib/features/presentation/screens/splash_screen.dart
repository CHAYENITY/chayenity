import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/features/auth/providers/auth_provider.dart';
import 'package:hourz/shared/constants/assets.dart';
import 'package:hourz/shared/constants/app_routes.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();

    // Initialize animations
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutBack),
    );

    // Start animation and check authentication
    _startSplashSequence();
  }

  void _startSplashSequence() async {
    // Start animations
    _animationController.forward();

    // Wait for minimum splash duration (for branding)
    await Future.delayed(const Duration(seconds: 2));

    // Check authentication status
    if (mounted) {
      final route = await ref.read(authProvider.notifier).checkAuthStatus();

      if (mounted) {
        if (route == 'dashboard') {
          context.go(AppRoutePath.dashboard);
        } else if (route == 'profileSetup') {
          context.go(AppRoutePath.profileSetup);
        } else {
          context.go(AppRoutePath.login);
        }
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return Center(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: ScaleTransition(
                scale: _scaleAnimation,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo Section
                    _buildLogo(),

                    const SizedBox(height: 18),

                    // Tagline
                    _buildTagline(),

                    const SizedBox(height: 36),

                    // Loading Indicator
                    _buildLoadingIndicator(),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildLogo() {
    return Column(
      children: [
        // Logo Image
        Image.asset(
          Assets.hourzLightImage,
          width: 130,
          height: 50,
          fit: BoxFit.contain,
        ),
      ],
    );
  }

  Widget _buildTagline() {
    return Text(
      'เพื่อนช่วยงานง่าย ได้ทุกชั่วโมง',
      style: TextStyle(
        fontSize: 14,
        color: const Color(0xFF111827),
        fontWeight: FontWeight.w500,
        height: 1.0,
        letterSpacing: 0.0,
      ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildLoadingIndicator() {
    return SizedBox(
      width: 40,
      height: 40,
      child: CircularProgressIndicator(
        strokeCap: StrokeCap.round,
        strokeWidth: 4,
        valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF14B8A6)),
      ),
    );
  }
}
