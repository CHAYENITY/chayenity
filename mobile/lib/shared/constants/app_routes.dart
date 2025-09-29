abstract class AppRoutePath {
  static const String root = '/'; // หน้าหลัก (TaskListScreen)
  static const String login = '/login'; // หน้าที่ไม่มี Shell (อนาคต)
  static const String home = '/home'; // อนาคต
  static const String profile = '/profile/:userId'; // Path Parameter (อนาคต)

  // Example Feature Routes
  static const String tasks = '/'; // หน้าหลักแสดง tasks
  static const String addTask = '/add-task'; // หน้าเพิ่ม task
  static const String editTask = '/edit-task'; // หน้าแก้ไข task
}

// สำหรับใช้ใน context.goNamed() หรือ GoRoute name
abstract class AppRouteName {
  static const String root = 'root';
  static const String login = 'login';
  static const String home = 'home';
  static const String profile = 'profile';

  // Example Feature Route Names
  static const String tasks = 'tasks';
  static const String addTask = 'addTask';
  static const String editTask = 'editTask';
}
