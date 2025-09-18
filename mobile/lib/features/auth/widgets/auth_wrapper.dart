import '../screens/login_screen.dart';

import 'package:flutter/material.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Check if we have authentication data
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // If user is SignIn, show home screen (you can replace this with your home screen)
        if (snapshot.hasData && snapshot.data != null) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('ยินดีต้อนรับ'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.logout),
                  onPressed: () async {
                    await FirebaseAuth.instance.signOut();
                  },
                ),
              ],
            ),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'ยินดีต้อนรับ ${snapshot.data?.email}',
                    style: const TextStyle(fontSize: 18),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'Email verified: ${snapshot.data?.emailVerified}',
                    style: TextStyle(
                      color: snapshot.data?.emailVerified == true
                          ? Colors.green
                          : Colors.orange,
                    ),
                  ),
                  if (snapshot.data?.emailVerified == false) ...[
                    const SizedBox(height: 10),
                    ElevatedButton(
                      onPressed: () async {
                        await snapshot.data?.sendEmailVerification();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('ส่งอีเมลยืนยันแล้ว')),
                          );
                        }
                      },
                      child: const Text('ส่งอีเมลยืนยันอีกครั้ง'),
                    ),
                  ],
                ],
              ),
            ),
          );
        }

        // If user is not SignIn in, show SignIn screen
        return const SignInScreen();
      },
    );
  }
}
