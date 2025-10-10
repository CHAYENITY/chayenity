import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';

import 'screens/login_screen.dart';
import 'screens/register_screen.dart';

/// Auth Feature Routes
final authRoutes = [
  GoRoute(
    path: AppRoutePath.register,
    name: AppRouteName.register,
    builder: (context, state) => const RegisterScreen(),
  ),
  GoRoute(
    path: AppRoutePath.login,
    name: AppRouteName.login,
    builder: (context, state) => const LoginScreen(),
  ),
];
