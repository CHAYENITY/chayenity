import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import './screens/index.dart';
import './models/index.dart';

final exampleRoutes = [
  // หน้าหลักแสดงรายการ tasks
  GoRoute(
    path: AppRoutePath.tasks,
    name: AppRouteName.tasks,
    builder: (context, state) => const TaskListScreen(),
  ),

  // หน้าเพิ่ม task ใหม่
  GoRoute(
    path: AppRoutePath.addTask,
    name: AppRouteName.addTask,
    builder: (context, state) => const AddTaskScreen(),
  ),

  // หน้าแก้ไข task (รับ task object ผ่าน extra parameter)
  GoRoute(
    path: AppRoutePath.editTask,
    name: AppRouteName.editTask,
    builder: (context, state) {
      final task = state.extra as Task?;
      if (task == null) {
        // ถ้าไม่มี task data ให้กลับไปหน้าหลัก
        return const TaskListScreen();
      }
      return EditTaskScreen(task: task);
    },
  ),
];
