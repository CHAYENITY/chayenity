import 'package:go_router/go_router.dart';

import 'package:hourz/shared/constants/app_routes.dart';

import 'screens/profile_setup_screen.dart';
import 'screens/profile_setup_step1_screen.dart';
import 'screens/profile_setup_step2_screen.dart';
import 'screens/profile_setup_step3_screen.dart';

final profileSetupRoutes = [
  GoRoute(
    path: AppRoutePath.profileSetup,
    name: AppRouteName.profileSetup,
    builder: (context, state) => const ProfileSetupScreen(),
  ),
  GoRoute(
    path: AppRoutePath.profileSetupStep1,
    name: AppRouteName.profileSetupStep1,
    builder: (context, state) => const ProfileSetupStep1Screen(),
  ),
  GoRoute(
    path: AppRoutePath.profileSetupStep2,
    name: AppRouteName.profileSetupStep2,
    builder: (context, state) => const ProfileSetupStep2Screen(),
  ),
  GoRoute(
    path: AppRoutePath.profileSetupStep3,
    name: AppRouteName.profileSetupStep3,
    builder: (context, state) => const ProfileSetupStep3Screen(),
  ),
];
