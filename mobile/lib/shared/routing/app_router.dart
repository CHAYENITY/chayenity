// lib/shared/routing/app_router.dart

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/features/dashboard/dashboard_routes.dart';
import 'package:hourz/features/_example/example_routes.dart';
import 'package:hourz/features/presentation/presentation_routes.dart';
import 'package:hourz/features/auth/auth_routes.dart';
import 'package:hourz/features/profile_setup/profile_setup_routes.dart';

import '../constants/app_routes.dart';
import '../screens/error_screen.dart';
import '../screens/dev_screen.dart';

// Key สำหรับ Root Navigator (สำหรับ Full-screen, Overlay)
final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>();

// Key สำหรับ Shell Navigator (สำหรับ Bottom/Side Bar)
final GlobalKey<NavigatorState> _shellNavigatorKey =
    GlobalKey<NavigatorState>();

/// Get the root navigator key for global access
GlobalKey<NavigatorState> get rootNavigatorKey => _rootNavigatorKey;

/// Get the shell navigator key for nested navigation
GlobalKey<NavigatorState> get shellNavigatorKey => _shellNavigatorKey;

class AppRouter {
  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: AppRoutePath.dev, // เปลี่ยนเป็นหน้า dev สำหรับ development
    // Global error handling
    errorBuilder: (context, state) =>
        ErrorScreen(error: 'Route not found: ${state.uri.path}'),

    routes: [
      // Developer Navigation (เป็นหน้าแรกสำหรับ development)
      GoRoute(
        path: AppRoutePath.dev,
        name: AppRouteName.dev,
        builder: (context, state) => const DevScreen(),
      ),

      // Example Feature Routes
      ...exampleRoutes,

      // Presentation Feature Routes (Splash, Onboarding, Terms)
      ...presentationRoutes,

      // Auth Feature Routes (Login, Register)
      ...authRoutes,

      // Profile Setup Feature Routes (Profile Setup, Step 1, Step 2, Step 3)
      ...profileSetupRoutes,

      // Dashboard Feature Routes (Dashboard)
      ...dashboardRoutes,

      // Future: ShellRoute สำหรับหน้าที่มี BottomNavigationBar
      // ShellRoute(
      //   navigatorKey: _shellNavigatorKey,
      //   builder: (context, state, child) {
      //     return MyShellWidget(child: child);
      //   },
      //   routes: [
      //     ...exampleRoutes,
      //   ],
      // ),
    ],

    // Future: Global Redirect (เช่น Authentication Check)
    redirect: (context, state) {
      // Logic: ถ้าไม่ได้ล็อกอิน และไม่ใช่หน้าล็อกอิน ให้ไปหน้าล็อกอิน
      // final isLoggedIn = /* ... your auth check ... */;
      // if (!isLoggedIn &&
      //     state.matchedLocation != AppRoutePath.login &&
      //     state.matchedLocation != AppRoutePath.register) {
      //    return AppRoutePath.login;
      // }
      return null;
    },

    // Debug mode logging
    debugLogDiagnostics: true,
  );
}
