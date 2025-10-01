import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../constants/app_routes.dart';

class DevScreen extends ConsumerWidget {
  const DevScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🛠️ Developer Navigation'),
        backgroundColor: Colors.orange.shade800,
        foregroundColor: Colors.white,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.orange.shade50, Colors.orange.shade100],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _DevHeader(),

              const SizedBox(height: 20),

              // Presentation Section
              _DevSection(
                title: '🎯 Presentation',
                color: Colors.purple,
                routes: [
                  _DevRoute(
                    title: 'Splash Screen',
                    subtitle: 'หน้า Splash (หน้าแรก)',
                    path: AppRoutePath.root,
                    icon: Icons.flash_on,
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Auth Section
              _DevSection(
                title: '🔐 Authentication',
                color: Colors.blue,
                routes: [
                  _DevRoute(
                    title: 'Login Screen',
                    subtitle: 'หน้าเข้าสู่ระบบ',
                    path: AppRoutePath.login,
                    icon: Icons.login,
                  ),
                  _DevRoute(
                    title: 'Register Screen',
                    subtitle: 'หน้าสมัครสมาชิก',
                    path: AppRoutePath.register,
                    icon: Icons.person_add,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Presentation Section
              _DevSection(
                title: '🎯 Dashboard',
                color: Colors.purple,
                routes: [
                  _DevRoute(
                    title: 'Dashboard',
                    subtitle: 'หน้า Dashboard',
                    path: AppRoutePath.dashboard,
                    icon: Icons.home,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Profile Setup Section
              _DevSection(
                title: '🔐 Profile Setup',
                color: Colors.blue,
                routes: [
                  _DevRoute(
                    title: 'Profile Setup Screen',
                    subtitle: 'หน้าเริ่มต้นตั้งค่าโปรไฟล์',
                    path: AppRoutePath.profileSetup,
                    icon: Icons.verified_user_outlined,
                  ),
                  _DevRoute(
                    title: 'Profile Setup Step 1 Screen',
                    subtitle: 'หน้าตั้งค่าโปรไฟล์ขั้นตอนที่ 1',
                    path: AppRoutePath.profileSetupStep1,
                    icon: Icons.verified_user_outlined,
                  ),
                  _DevRoute(
                    title: 'Profile Setup Step 2 Screen',
                    subtitle: 'หน้าตั้งค่าโปรไฟล์ขั้นตอนที่ 2',
                    path: AppRoutePath.profileSetupStep2,
                    icon: Icons.verified_user_outlined,
                  ),
                  _DevRoute(
                    title: 'Profile Setup Step 3 Screen',
                    subtitle: 'หน้าตั้งค่าโปรไฟล์ขั้นตอนที่ 3',
                    path: AppRoutePath.profileSetupStep3,
                    icon: Icons.verified_user_outlined,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Example/Tasks Section
              _DevSection(
                title: '📝 Example Features',
                color: Colors.green,
                routes: [
                  _DevRoute(
                    title: 'Tasks List',
                    subtitle: 'หน้าแสดงรายการ Tasks',
                    path: AppRoutePath.tasks,
                    icon: Icons.list_alt,
                  ),
                  _DevRoute(
                    title: 'Add Task',
                    subtitle: 'หน้าเพิ่ม Task ใหม่',
                    path: AppRoutePath.addTask,
                    icon: Icons.add_task,
                  ),
                  _DevRoute(
                    title: 'Edit Task',
                    subtitle: 'หน้าแก้ไข Task',
                    path: AppRoutePath.editTask,
                    icon: Icons.edit,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Future Features Section
              _DevSection(
                title: '🚀 Future Features',
                color: Colors.grey,
                routes: [
                  _DevRoute(
                    title: 'Developer Screen',
                    subtitle: 'หน้านี้เอง (สำหรับทดสอบ)',
                    path: AppRoutePath.dev,
                    icon: Icons.developer_mode,
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // Developer Actions
              _DevActionsSection(),

              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}

// Header Widget
class _DevHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withAlpha(10),
                  spreadRadius: 2,
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                const Icon(
                  Icons.developer_mode,
                  size: 48,
                  color: Colors.orange,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Developer Navigation',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'สำหรับทดสอบการนำทางไปยังหน้าต่างๆ ในแอป',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// Section Widget
class _DevSection extends StatelessWidget {
  final String title;
  final Color color;
  final List<_DevRoute> routes;

  const _DevSection({
    required this.title,
    required this.color,
    required this.routes,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withAlpha(10),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withAlpha(10),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color.withAlpha(80),
              ),
            ),
          ),
          ...routes.map(
            (route) => _DevRouteCard(route: route, sectionColor: color),
          ),
        ],
      ),
    );
  }
}

// Route Data Class
class _DevRoute {
  final String title;
  final String subtitle;
  final String path;
  final IconData icon;
  final bool isDisabled;

  const _DevRoute({
    required this.title,
    required this.subtitle,
    required this.path,
    required this.icon,
    // ignore: unused_element_parameter
    this.isDisabled = false,
  });
}

// Route Card Widget
class _DevRouteCard extends ConsumerWidget {
  final _DevRoute route;
  final Color sectionColor;

  const _DevRouteCard({required this.route, required this.sectionColor});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.only(left: 16, right: 16, bottom: 12),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: route.isDisabled
              ? null
              : () {
                  try {
                    context.go(route.path);
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Error navigating to ${route.path}: $e'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                },
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(
                color: route.isDisabled
                    ? Colors.grey.shade300
                    : sectionColor.withAlpha(30),
              ),
              borderRadius: BorderRadius.circular(8),
              color: route.isDisabled
                  ? Colors.grey.shade50
                  : sectionColor.withAlpha(5),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: route.isDisabled
                        ? Colors.grey.shade200
                        : sectionColor.withAlpha(10),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    route.icon,
                    color: route.isDisabled ? Colors.grey : sectionColor,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        route.title,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: route.isDisabled
                              ? Colors.grey
                              : Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        route.subtitle,
                        style: TextStyle(
                          fontSize: 14,
                          color: route.isDisabled
                              ? Colors.grey.shade400
                              : Colors.grey[600],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        route.path,
                        style: TextStyle(
                          fontSize: 12,
                          color: route.isDisabled
                              ? Colors.grey.shade400
                              : sectionColor,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  route.isDisabled ? Icons.block : Icons.arrow_forward_ios,
                  color: route.isDisabled ? Colors.grey.shade400 : Colors.grey,
                  size: 16,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// Developer Actions Section
class _DevActionsSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withAlpha(10),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.red.withAlpha(10),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Text(
              '⚡ Developer Actions',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.red.withAlpha(80),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _ActionButton(
                  title: 'Clear App Data',
                  subtitle: 'ล้างข้อมูลแอป (SharedPreferences)',
                  icon: Icons.clear_all,
                  color: Colors.red,
                  onPressed: () {
                    // TODO: Implement clear app data
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Clear app data (Not implemented yet)'),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 12),
                _ActionButton(
                  title: 'Toggle Theme',
                  subtitle: 'สลับธีม Light/Dark',
                  icon: Icons.brightness_6,
                  color: Colors.orange,
                  onPressed: () {
                    // TODO: Implement theme toggle
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Toggle theme (Not implemented yet)'),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 12),
                _ActionButton(
                  title: 'Show App Info',
                  subtitle: 'แสดงข้อมูลแอป และ packages',
                  icon: Icons.info_outline,
                  color: Colors.blue,
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('App Information'),
                        content: const Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('🏗️ Architecture: Feature-based'),
                            Text('📱 Framework: Flutter'),
                            Text('🔄 State: Riverpod'),
                            Text('🧊 Models: Freezed'),
                            Text('🛣️ Routing: Go Router'),
                            Text('🌐 HTTP: Dio'),
                          ],
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(),
                            child: const Text('Close'),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Action Button Widget
class _ActionButton extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(color: color.withAlpha(30)),
            borderRadius: BorderRadius.circular(8),
            color: color.withAlpha(5),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withAlpha(10),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, color: Colors.grey, size: 14),
            ],
          ),
        ),
      ),
    );
  }
}
