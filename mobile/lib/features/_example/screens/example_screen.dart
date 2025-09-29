import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import 'package:hourz/shared/utils/common_utils.dart' as app_utils;
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
    // Watch states
    final tasks = ref.watch(taskListProvider);
    final taskStats = ref.watch(taskStatsProvider);
    final isLoading = ref.watch(isTasksLoadingProvider);
    final isActionLoading = ref.watch(isTaskActionLoadingProvider);
    final currentError = ref.watch(errorProvider);

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
          // Error display
          if (currentError != null)
            Container(
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
            ),

          // Task Statistics Card
          Container(
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
                  value: taskStats['total'].toString(),
                  color: AppColors.primary,
                ),
                _StatItem(
                  icon: Icons.check_circle,
                  label: 'Completed',
                  value: taskStats['completed'].toString(),
                  color: AppColors.accentGreen1,
                ),
                _StatItem(
                  icon: Icons.radio_button_unchecked,
                  label: 'Pending',
                  value: taskStats['pending'].toString(),
                  color: AppColors.accentOrange,
                ),
              ],
            ),
          ),

          // Loading indicator
          if (isLoading) const LinearProgressIndicator(),

          // Task List
          Expanded(
            child: tasks.isEmpty && !isLoading
                ? const _EmptyState()
                : RefreshIndicator(
                    onRefresh: () =>
                        ref.read(taskListProvider.notifier).refreshTasks(),
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: tasks.length,
                      itemBuilder: (context, index) {
                        final task = tasks[index];
                        return TaskCard(
                          task: task,
                          isDisabled: isActionLoading,
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: isLoading || isActionLoading
            ? null
            : () {
                // Navigate to Add Task screen using Go Router context
                context.go(AppRoutePath.addTask);
              },
        tooltip: 'Add Task',
        child: const Icon(Icons.add),
      ),
    );
  }
}

/// 📊 Statistics Item Widget
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
class AddTaskScreen extends ConsumerStatefulWidget {
  const AddTaskScreen({super.key});

  @override
  ConsumerState<AddTaskScreen> createState() => _AddTaskScreenState();
}

class _AddTaskScreenState extends ConsumerState<AddTaskScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      ref
          .read(taskListProvider.notifier)
          .createTask(
            title: _titleController.text.trim(),
            description: _descriptionController.text.trim(),
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = ref.watch(isLoadingProvider('create-task'));

    return Scaffold(
      appBar: AppBar(
        title: const Text('➕ Add Task'),
        actions: [
          TextButton.icon(
            onPressed: isLoading ? null : _submitForm,
            icon: const Icon(Icons.save),
            label: const Text('Save'),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Loading indicator
              if (isLoading) const LinearProgressIndicator(),

              const SizedBox(height: 16),

              // Title field
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'Title *',
                  hintText: 'Enter task title',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.title),
                ),
                validator: (value) =>
                    app_utils.ValidationUtils.validateRequired(value, 'Title'),
                textInputAction: TextInputAction.next,
                enabled: !isLoading,
              ),

              const SizedBox(height: 16),

              // Description field
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description *',
                  hintText: 'Enter task description',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.description),
                ),
                validator: (value) =>
                    app_utils.ValidationUtils.validateRequired(
                      value,
                      'Description',
                    ),
                maxLines: 3,
                textInputAction: TextInputAction.done,
                enabled: !isLoading,
                onFieldSubmitted: (_) => _submitForm(),
              ),

              const SizedBox(height: 24),

              // Save button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: isLoading ? null : _submitForm,
                  icon: isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.save),
                  label: Text(isLoading ? 'Creating...' : 'Create Task'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// ✏️ Edit Task Screen - หน้าจอแก้ไข task
class EditTaskScreen extends ConsumerStatefulWidget {
  final Task task;

  const EditTaskScreen({super.key, required this.task});

  @override
  ConsumerState<EditTaskScreen> createState() => _EditTaskScreenState();
}

class _EditTaskScreenState extends ConsumerState<EditTaskScreen> {
  late Task _editedTask;

  @override
  void initState() {
    super.initState();
    _editedTask = widget.task;
  }

  void _updateTask(String title, String description) {
    final updatedTask = _editedTask.copyWith(
      title: title,
      description: description,
    );

    ref.read(taskListProvider.notifier).updateTask(updatedTask);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('✏️ Edit Task'),
        actions: [
          // Delete button in app bar
          IconButton(
            onPressed: () {
              _showDeleteConfirmation(context);
            },
            icon: const Icon(Icons.delete),
            color: AppColors.error,
            tooltip: 'Delete Task',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: TaskForm(
          initialTask: _editedTask,
          title: 'Update Task',
          onSubmit: _updateTask,
        ),
      ),
    );
  }

  void _showDeleteConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Task'),
        content: Text(
          'Are you sure you want to delete "${_editedTask.title}"?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              context.pop(); // Close edit screen using Go Router
              ref.read(taskListProvider.notifier).deleteTask(_editedTask.id);
            },
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
