import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import '../models/example.dart';
import '../services/example_service.dart';

// * Task Service Provider
final taskServiceProvider = Provider<TaskService>((ref) {
  final apiService = ref.read(apiProvider);
  return TaskService(apiService);
});

// * Task List State Notifier
class TaskListNotifier extends StateNotifier<List<Task>> {
  TaskListNotifier(this._ref) : super([]);
  final Ref _ref;

  Future<void> loadTasks() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('load-tasks');
      final taskService = _ref.read(taskServiceProvider);
      final tasks = await taskService.getTasks();
      state = tasks;
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Failed to load tasks: $e', context: 'loadTasks');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('load-tasks');
    }
  }

  Future<void> createTask({
    required String title,
    required String description,
  }) async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('create-task');
      final taskService = _ref.read(taskServiceProvider);

      // * Create a new task instance
      final newTask = Task(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        title: title,
        description: description,
        createdAt: DateTime.now(),
      );

      final createdTask = await taskService.createTask(newTask);
      state = [...state, createdTask];
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Failed to create task: $e', context: 'createTask');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('create-task');
    }
  }

  Future<void> updateTask(Task updatedTask) async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('update-task');
      final taskService = _ref.read(taskServiceProvider);
      final updated = await taskService.updateTask(updatedTask);
      state = state.map((t) => t.id == updatedTask.id ? updated : t).toList();
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Failed to update task: $e', context: 'updateTask');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('update-task');
    }
  }

  Future<void> deleteTask(String taskId) async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('delete-task');
      final taskService = _ref.read(taskServiceProvider);
      await taskService.deleteTask(taskId);
      state = state.where((task) => task.id != taskId).toList();
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Failed to delete task: $e', context: 'deleteTask');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('delete-task');
    }
  }

  Future<void> toggleTaskCompletion(String taskId) async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('toggle-task');
      final taskService = _ref.read(taskServiceProvider);
      final updatedTask = await taskService.toggleTaskCompletion(taskId);
      state = state.map((t) => t.id == taskId ? updatedTask : t).toList();
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Failed to toggle task: $e', context: 'toggleTask');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('toggle-task');
    }
  }

  Future<void> refreshTasks() async {
    await loadTasks();
  }
}

final taskListProvider = StateNotifierProvider<TaskListNotifier, List<Task>>((
  ref,
) {
  return TaskListNotifier(ref);
});

// ⚡ Use .select() for computed values - no rebuild unless value changes
final taskStatsProvider = Provider<Map<String, int>>((ref) {
  final tasks = ref.watch(taskListProvider);
  final completed = tasks.where((task) => task.isCompleted).length;
  final pending = tasks.where((task) => !task.isCompleted).length;
  return {'total': tasks.length, 'completed': completed, 'pending': pending};
});

// ⚡ Specific loading state providers
final isTasksLoadingProvider = Provider<bool>((ref) {
  return ref.watch(isLoadingProvider('load-tasks'));
});

final isTaskActionLoadingProvider = Provider<bool>((ref) {
  final isCreating = ref.watch(isLoadingProvider('create-task'));
  final isUpdating = ref.watch(isLoadingProvider('update-task'));
  final isDeleting = ref.watch(isLoadingProvider('delete-task'));
  final isToggling = ref.watch(isLoadingProvider('toggle-task'));
  return isCreating || isUpdating || isDeleting || isToggling;
});
