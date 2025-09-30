import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import 'package:hourz/shared/utils/common_utils.dart' as app_utils;
import '../models/example.dart';
import '../providers/example_providers.dart';

/// 🎴 Task Card Widget - แสดงข้อมูล task ในรูปแบบ card
class TaskCard extends ConsumerWidget {
  final Task task;
  final bool isDisabled;

  const TaskCard({super.key, required this.task, this.isDisabled = false});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: task.isCompleted
            ? AppColors.primary.withAlpha(10)
            : theme.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: task.isCompleted
              ? AppColors.primary.withAlpha(30)
              : Colors.grey.withAlpha(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(5),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: InkWell(
        onTap: isDisabled
            ? null
            : () {
                // Navigate to task detail/edit screen
                _showTaskActions(context, ref);
              },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row with title and status
              Row(
                children: [
                  // Completion checkbox
                  Checkbox(
                    value: task.isCompleted,
                    onChanged: isDisabled
                        ? null
                        : (value) {
                            ref
                                .read(taskListProvider.notifier)
                                .toggleTaskCompletion(task.id);
                          },
                    activeColor: AppColors.primary,
                  ),

                  // Title
                  Expanded(
                    child: Text(
                      task.title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        decoration: task.isCompleted
                            ? TextDecoration.lineThrough
                            : TextDecoration.none,
                        color: task.isCompleted ? Colors.grey.shade600 : null,
                      ),
                    ),
                  ),

                  // Status badge
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: task.isCompleted
                          ? AppColors.primary
                          : AppColors.secondary,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      task.isCompleted ? 'Done' : 'Pending',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Description
              if (task.description.isNotEmpty) ...[
                Text(
                  task.description,
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 14,
                    decoration: task.isCompleted
                        ? TextDecoration.lineThrough
                        : TextDecoration.none,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),
              ],

              // Footer with date and actions
              Row(
                children: [
                  // Created date
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: Colors.grey.shade500,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    app_utils.DateUtils.formatDateTime(task.createdAt),
                    style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                  ),

                  // Completed date (if completed)
                  if (task.isCompleted && task.completedAt != null) ...[
                    const SizedBox(width: 16),
                    Icon(
                      Icons.check_circle,
                      size: 16,
                      color: AppColors.primary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Done ${app_utils.DateUtils.formatDateTime(task.completedAt!)}',
                      style: TextStyle(
                        color: AppColors.primary,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],

                  const Spacer(),

                  // Action buttons
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Edit button
                      IconButton(
                        onPressed: isDisabled
                            ? null
                            : () {
                                _editTask(context, ref);
                              },
                        icon: const Icon(Icons.edit),
                        iconSize: 20,
                        tooltip: 'Edit Task',
                        color: AppColors.primary,
                      ),

                      // Delete button
                      IconButton(
                        onPressed: isDisabled
                            ? null
                            : () {
                                _deleteTask(context, ref);
                              },
                        icon: const Icon(Icons.delete),
                        iconSize: 20,
                        tooltip: 'Delete Task',
                        color: AppColors.destructive,
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Show task action bottom sheet
  void _showTaskActions(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      builder: (context) => TaskActionSheet(task: task),
    );
  }

  /// Edit task
  void _editTask(BuildContext context, WidgetRef ref) {
    context.go(AppRoutePath.editTask, extra: task);
  }

  /// Delete task with confirmation
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
              ref.read(taskListProvider.notifier).deleteTask(task.id);
            },
            style: TextButton.styleFrom(foregroundColor: AppColors.destructive),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

/// 📋 Task Action Sheet - แสดง actions สำหรับ task
class TaskActionSheet extends ConsumerWidget {
  final Task task;

  const TaskActionSheet({super.key, required this.task});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          const SizedBox(height: 16),

          // Task info
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: task.isCompleted
                      ? AppColors.primary.withAlpha(20)
                      : AppColors.secondary.withAlpha(20),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  task.isCompleted
                      ? Icons.check_circle
                      : Icons.radio_button_unchecked,
                  color: task.isCompleted
                      ? AppColors.primary
                      : AppColors.secondary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (task.description.isNotEmpty)
                      Text(
                        task.description,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 14,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Actions
          Column(
            children: [
              // Toggle completion
              ListTile(
                leading: Icon(
                  task.isCompleted ? Icons.undo : Icons.check_circle,
                  color: task.isCompleted
                      ? AppColors.secondary
                      : AppColors.primary,
                ),
                title: Text(
                  task.isCompleted ? 'Mark as Pending' : 'Mark as Complete',
                ),
                onTap: () {
                  Navigator.pop(context);
                  ref
                      .read(taskListProvider.notifier)
                      .toggleTaskCompletion(task.id);
                },
              ),

              // Edit
              ListTile(
                leading: Icon(Icons.edit, color: AppColors.primary),
                title: const Text('Edit Task'),
                onTap: () {
                  Navigator.pop(context);
                  context.go(AppRoutePath.editTask, extra: task);
                },
              ),

              // Delete
              ListTile(
                leading: Icon(Icons.delete, color: AppColors.destructive),
                title: const Text('Delete Task'),
                onTap: () {
                  Navigator.pop(context);
                  _showDeleteConfirmation(context, ref);
                },
              ),
            ],
          ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }

  void _showDeleteConfirmation(BuildContext context, WidgetRef ref) {
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
              ref.read(taskListProvider.notifier).deleteTask(task.id);
            },
            style: TextButton.styleFrom(foregroundColor: AppColors.destructive),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

/// 📝 Task Form Widget - สำหรับการเพิ่ม/แก้ไข task
class TaskForm extends ConsumerStatefulWidget {
  final Task? initialTask;
  final String title;
  final void Function(String title, String description) onSubmit;

  const TaskForm({
    super.key,
    this.initialTask,
    required this.title,
    required this.onSubmit,
  });

  @override
  ConsumerState<TaskForm> createState() => _TaskFormState();
}

class _TaskFormState extends ConsumerState<TaskForm> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(
      text: widget.initialTask?.title ?? '',
    );
    _descriptionController = TextEditingController(
      text: widget.initialTask?.description ?? '',
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      widget.onSubmit(
        _titleController.text.trim(),
        _descriptionController.text.trim(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = ref.watch(isTaskActionLoadingProvider);

    return Form(
      key: _formKey,
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
            validator: (value) => app_utils.ValidationUtils.validateRequired(
              value,
              'Description',
            ),
            maxLines: 3,
            textInputAction: TextInputAction.done,
            enabled: !isLoading,
            onFieldSubmitted: (_) => _submitForm(),
          ),

          const SizedBox(height: 24),

          // Submit button
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
              label: Text(
                isLoading
                    ? (widget.initialTask != null
                          ? 'Updating...'
                          : 'Creating...')
                    : widget.title,
              ),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.all(16),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
