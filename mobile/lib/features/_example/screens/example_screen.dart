import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import '../models/example.dart';
import '../providers/example_providers.dart';
import '../widgets/example_widgets.dart';

/// 📋 Task List Screen - หน้าจอหลักสำหรับแสดงรายการ tasks
class TaskListScreen extends ConsumerStatefulWidget {
  const TaskListScreen({super.key});

  @override
  ConsumerState<TaskListScreen> createState() => _TaskListScreenState();
}

class _TaskListScreenState extends ConsumerState<TaskListScreen> {
  @override
  void initState() {
    super.initState();
    // โหลด tasks เมื่อเข้าหน้า
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(taskListProvider.notifier).loadTasks();
    });
  }

  @override
  Widget build(BuildContext context) {
    // ⚡ Use derived providers - rebuilds only when specific values change
    final isLoading = ref.watch(isTasksLoadingProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('📋 Tasks'),
        actions: [
          // Theme toggle button
          IconButton(
            icon: const Icon(Icons.brightness_6),
            tooltip: 'Toggle Theme',
            onPressed: () {
              ref.read(themeModeProvider.notifier).toggleTheme();
            },
          ),
          // Refresh button
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Tasks',
            onPressed: isLoading
                ? null
                : () {
                    ref.read(taskListProvider.notifier).refreshTasks();
                  },
          ),
        ],
      ),
      body: Column(
        children: [
          // Error display (rebuilds only when error changes)
          const _ErrorDisplay(),

          // Task Statistics Card (rebuilds only when stats change)
          const _StatsCard(),

          // Loading indicator
          if (isLoading) const LinearProgressIndicator(),

          // Task List (rebuilds only when list changes)
          const Expanded(child: _TaskListView()),
        ],
      ),
      floatingActionButton: const _AddTaskButton(),
    );
  }
}

/// � Error Display Widget (rebuilds only when error changes)
class _ErrorDisplay extends ConsumerWidget {
  const _ErrorDisplay();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentError = ref.watch(errorProvider);

    if (currentError == null) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade600),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Error occurred',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade800,
                  ),
                ),
                Text(
                  currentError.message,
                  style: TextStyle(color: Colors.red.shade700),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close),
            color: Colors.red.shade600,
            onPressed: () {
              ref.read(errorProvider.notifier).clearError();
            },
          ),
        ],
      ),
    );
  }
}

/// �📊 Stats Card Widget (rebuilds only when stats change)
class _StatsCard extends ConsumerWidget {
  const _StatsCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ⚡ Watch only the stats - no rebuild when list items change
    final totalCount = ref.watch(taskStatsProvider.select((s) => s['total']!));
    final completedCount = ref.watch(
      taskStatsProvider.select((s) => s['completed']!),
    );
    final pendingCount = ref.watch(
      taskStatsProvider.select((s) => s['pending']!),
    );

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(5),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _StatItem(
            icon: Icons.list_alt,
            label: 'Total',
            value: totalCount.toString(),
            color: AppColors.primary,
          ),
          _StatItem(
            icon: Icons.check_circle,
            label: 'Completed',
            value: completedCount.toString(),
            color: AppColors.primary,
          ),
          _StatItem(
            icon: Icons.radio_button_unchecked,
            label: 'Pending',
            value: pendingCount.toString(),
            color: AppColors.secondaryForeground,
          ),
        ],
      ),
    );
  }
}

/// 📋 Task List View Widget (rebuilds only when list changes)
class _TaskListView extends ConsumerWidget {
  const _TaskListView();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasks = ref.watch(taskListProvider);
    final isLoading = ref.watch(isTasksLoadingProvider);
    final isActionLoading = ref.watch(isTaskActionLoadingProvider);

    if (tasks.isEmpty && !isLoading) {
      return const _EmptyState();
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(taskListProvider.notifier).refreshTasks(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: tasks.length,
        itemBuilder: (context, index) {
          final task = tasks[index];
          return TaskCard(task: task, isDisabled: isActionLoading);
        },
      ),
    );
  }
}

/// ➕ Add Task Button Widget (rebuilds only when loading states change)
class _AddTaskButton extends ConsumerWidget {
  const _AddTaskButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isLoading = ref.watch(isTasksLoadingProvider);
    final isActionLoading = ref.watch(isTaskActionLoadingProvider);

    return FloatingActionButton(
      onPressed: isLoading || isActionLoading
          ? null
          : () {
              context.go(AppRoutePath.addTask);
            },
      tooltip: 'Add Task',
      child: const Icon(Icons.add),
    );
  }
}

/// 📊 Statistics Item Widget (static, never rebuilds unless parent changes)
class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}

/// 📭 Empty State Widget
class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.task_alt, size: 80, color: Colors.grey.shade300),
          const SizedBox(height: 16),
          Text(
            'No tasks yet',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Tap the + button to add your first task',
            style: TextStyle(color: Colors.grey.shade500),
          ),
        ],
      ),
    );
  }
}

/// ➕ Add Task Screen - หน้าจอเพิ่ม task ใหม่
class AddTaskScreen extends ConsumerWidget {
  const AddTaskScreen({super.key});

  void _createTask(WidgetRef ref, String title, String description) {
    ref
        .read(taskListProvider.notifier)
        .createTask(title: title, description: description);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('➕ Add Task')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: TaskForm(
          title: 'Create Task',
          onSubmit: (title, description) =>
              _createTask(ref, title, description),
        ),
      ),
    );
  }
}

/// ✏️ Edit Task Screen - หน้าจอแก้ไข task
class EditTaskScreen extends ConsumerWidget {
  final Task task;

  const EditTaskScreen({super.key, required this.task});

  void _updateTask(WidgetRef ref, String title, String description) {
    final updatedTask = task.copyWith(title: title, description: description);
    ref.read(taskListProvider.notifier).updateTask(updatedTask);
  }

  void _deleteTask(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Task'),
        content: Text('Are you sure you want to delete "${task.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
              ref.read(taskListProvider.notifier).deleteTask(task.id);
            },
            style: TextButton.styleFrom(foregroundColor: AppColors.destructive),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('✏️ Edit Task'),
        actions: [
          IconButton(
            onPressed: () => _deleteTask(context, ref),
            icon: const Icon(Icons.delete),
            color: AppColors.destructive,
            tooltip: 'Delete Task',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: TaskForm(
          initialTask: task,
          title: 'Update Task',
          onSubmit: (title, description) =>
              _updateTask(ref, title, description),
        ),
      ),
    );
  }
}
