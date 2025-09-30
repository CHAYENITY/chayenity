abstract class AppRoutePath {
  static const String root = '/'; // หน้า Splash Screen
  static const String dev = '/dev'; // หน้า Developer Navigation
  static const String onboarding = '/onboarding';

  // Auth
  static const String login = '/login';
  static const String register = '/register'; // หน้า Register

  // Profile Setup
  static const String profileSetup = '/profile-setup';
  static const String profileSetupStep1 = '/profile-setup/step1';
  static const String profileSetupStep2 = '/profile-setup/step2';
  static const String profileSetupStep3 = '/profile-setup/step3';

  // Example Feature Routes
  static const String tasks = '/tasks'; // หน้าแสดง tasks
  static const String addTask = '/add-task'; // หน้าเพิ่ม task
  static const String editTask = '/edit-task'; // หน้าแก้ไข task
}

// สำหรับใช้ใน context.goNamed() หรือ GoRoute name
abstract class AppRouteName {
  static const String root = 'root';
  static const String dev = 'dev';
  static const String onboarding = 'onboarding';

  // Auth
  static const String login = 'login';
  static const String register = 'register';

  // Profile Setup
  static const String profileSetup = 'profileSetup';
  static const String profileSetupStep1 = 'profileSetupStep1';
  static const String profileSetupStep2 = 'profileSetupStep2';
  static const String profileSetupStep3 = 'profileSetupStep3';

  // Example Feature Route Names
  static const String tasks = 'tasks';
  static const String addTask = 'addTask';
  static const String editTask = 'editTask';
}
