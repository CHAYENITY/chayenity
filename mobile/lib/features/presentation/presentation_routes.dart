import 'package:go_router/go_router.dart';
import '../../shared/constants/app_routes.dart';
import 'screens/index.dart';

final presentationRoutes = [
  GoRoute(
    path: AppRoutePath.root,
    name: AppRouteName.root,
    builder: (context, state) => const SplashScreen(),
  ),
  GoRoute(
    path: AppRoutePath.onboarding,
    name: AppRouteName.onboarding,
    builder: (context, state) => const OnboardingScreen(),
  ),
];
