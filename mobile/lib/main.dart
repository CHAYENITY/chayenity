import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// * SCREEN
import 'package:chayenity/shared/screens/error_screen.dart';
import 'package:chayenity/features/auth/screens/login_screen.dart';
import 'package:chayenity/features/home/screens/home_screen.dart';
import 'package:chayenity/features/auth/providers/auth_providers.dart';
import 'package:chayenity/features/auth/models/auth_state.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    runApp(const ProviderScope(child: MainApp()));
  } catch (e) {
    runApp(ErrorScreen(error: e.toString()));
  }
}

class MainApp extends ConsumerStatefulWidget {
  const MainApp({super.key});

  @override
  ConsumerState<MainApp> createState() => _MainAppState();
}

class _MainAppState extends ConsumerState<MainApp> {
  @override
  void initState() {
    super.initState();
    // Initialize auth state
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(authProvider.notifier).initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chayenity',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
      ),
      home: Consumer(
        builder: (context, ref, child) {
          final authState = ref.watch(authProvider);

          // Show loading screen during initial auth check
          if (authState.status == AuthStatus.initial) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }

          // Navigate based on authentication status
          if (authState.isAuthenticated) {
            return const HomeScreen();
          } else {
            return const LoginScreen();
          }
        },
      ),
    );
  }
}
