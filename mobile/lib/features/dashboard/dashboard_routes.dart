import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import './screens/dashboard_screen.dart';

final dashboardRoutes = [
  GoRoute(
    path: AppRoutePath.dashboard,
    name: AppRouteName.dashboard,
    builder: (context, state) => const DashboardScreen(),
  ),
];
