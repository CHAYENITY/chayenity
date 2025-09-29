import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// * GLOBAL PROVIDERS
import 'package:hourz/shared/providers/index.dart';

// * ROUTER
import 'package:hourz/shared/routing/app_router.dart';

// * SCREENS
import 'package:hourz/shared/screens/error_screen.dart';

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
  Widget build(BuildContext context) {
    // Watch theme providers
    final themeMode = ref.watch(themeModeProvider);
    final lightTheme = ref.watch(lightThemeProvider);
    final darkTheme = ref.watch(darkThemeProvider);

    return MaterialApp.router(
      title: AppConfig.appName,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: themeMode,

      // Use Go Router
      routerConfig: AppRouter.router,
    );
  }
}
