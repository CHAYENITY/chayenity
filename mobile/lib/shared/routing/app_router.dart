// lib/shared/routing/app_router.dart

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../constants/app_routes.dart';
import '../screens/error_screen.dart';
import '../../features/_example/example_routes.dart';

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
    initialLocation: AppRoutePath.root, // /
    // Global error handling
    errorBuilder: (context, state) =>
        ErrorScreen(error: 'Route not found: ${state.uri.path}'),

    routes: [
      // Example Feature Routes (ไม่ใช้ Shell สำหรับตอนนี้)
      ...exampleRoutes,

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

      // Future: Full-Screen Routes (เช่น Login)
      // GoRoute(
      //   path: AppRoutePath.login,
      //   name: AppRouteName.login,
      //   builder: (context, state) => const LoginScreen(),
      // ),
    ],

    // Future: Global Redirect (เช่น Authentication Check)
    redirect: (context, state) {
      // Logic: ถ้าไม่ได้ล็อกอิน และไม่ใช่หน้าล็อกอิน ให้ไปหน้าล็อกอิน
      // final isLoggedIn = /* ... your auth check ... */;
      // if (!isLoggedIn && state.matchedLocation != AppRoutePath.login) {
      //    return AppRoutePath.login;
      // }
      return null;
    },

    // Debug mode logging
    debugLogDiagnostics: true,
  );
}
