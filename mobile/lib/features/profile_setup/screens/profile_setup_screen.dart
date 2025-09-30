import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import '../providers/profile_setup_provider.dart';

class ProfileSetupScreen extends ConsumerWidget {
  const ProfileSetupScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Reset profile setup state when entering
    ref.read(profileSetupProvider.notifier).reset();

    // Navigate to step 1 immediately
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.push(AppRoutePath.profileSetupStep1);
    });

    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
