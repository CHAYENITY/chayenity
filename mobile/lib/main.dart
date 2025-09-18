import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'package:chayenity/shared/constants/env_config.dart';

// * SCREEN
import 'package:chayenity/shared/screens/error_screen.dart';
import 'package:chayenity/features/auth/screens/login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await dotenv.load(fileName: ".env");

    // Validate Firebase configuration
    EnvConfig.validateConfiguration();

    runApp(const MainApp());
  } catch (e) {
    runApp(ErrorScreen(error: e.toString()));
  }
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('อะไรนะ World!'),

              const SizedBox(height: 20),

              ElevatedButton(
                onPressed: () {
                  // กดแล้ว navigate ไป LoginScreen
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const LoginScreen(),
                    ),
                  );
                },
                child: const Text("ไปหน้า Login"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
