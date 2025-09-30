# 📖 Architecture Deep Dive - Hourz Flutter App

> **📝 สำหรับ Overview:** ดู [ARCHITECTURE.md](./ARCHITECTURE.md)  
> **🤖 สำหรับ AI Coding:** ดู [AI_CODING_GUIDE.md](./AI_CODING_GUIDE.md)

## 🌐 Global Services Implementation Details

### ApiService (`shared/services/api_service.dart`)

**HTTP client with error handling and logging**

**Features:**

- Generic CRUD operations
- Error handling with `ApiException`
- Request/Response logging
- Auth token management

**Usage Examples:**

```dart
final api = ref.read(apiProvider);

// GET List
final items = await api.getList('/items', Item.fromJson);

// GET by ID
final item = await api.getById('/items', '123', Item.fromJson);

// POST Create
final newItem = await api.create('/items', data, Item.fromJson);

// PUT Update
final updatedItem = await api.update('/items', '123', data, Item.fromJson);

// DELETE
await api.delete('/items', '123');

// Auth
api.setAuthToken('your-token');
api.clearAuthToken();
```

### ThemeProvider (`shared/providers/theme_provider.dart`)

**Light/Dark theme management**

**Providers:**

- `themeModeProvider` - Current theme mode
- `lightThemeProvider` - Light theme data
- `darkThemeProvider` - Dark theme data

**Usage:**

```dart
// Watch current theme
final themeMode = ref.watch(themeModeProvider);

// Change theme
ref.read(themeModeProvider.notifier).setThemeMode(ThemeMode.dark);
ref.read(themeModeProvider.notifier).toggleTheme();
```

### LoadingProvider (`shared/providers/loading_provider.dart`)

**Global loading states management**

**Providers:**

- `loadingProvider` - All loading states
- `isLoadingProvider.family` - Check specific loading
- `hasAnyLoadingProvider` - Check if any loading active

**Usage:**

```dart
// Start/Stop loading
ref.read(loadingProvider.notifier).startLoading('login');
ref.read(loadingProvider.notifier).stopLoading('login');

// Watch loading state
final isLoginLoading = ref.watch(isLoadingProvider('login'));
final hasAnyLoading = ref.watch(hasAnyLoadingProvider);

// Clear all
ref.read(loadingProvider.notifier).clearAll();
```

### ErrorProvider (`shared/providers/error_provider.dart`)

**Centralized error handling**

**Providers:**

- `errorProvider` - Current error state
- `hasErrorProvider` - Check if error exists

**Usage:**

```dart
// Handle errors
ref.read(errorProvider.notifier).handleError('Something went wrong');
ref.read(errorProvider.notifier).handleApiError(apiException, context: 'login');

// Watch errors
final currentError = ref.watch(errorProvider);
final hasError = ref.watch(hasErrorProvider);

// Clear error
ref.read(errorProvider.notifier).clearError();
```

## 🧊 Freezed Models Deep Dive

### Benefits

- **Immutability**: Prevents accidental data changes
- **copyWith()**: Create new instances with changes
- **Equality**: Built-in `==` and `hashCode`
- **toString()**: Debug-friendly string representation
- **JSON Serialization**: Integration with json_serializable
- **Union Types**: Support for sealed classes

### Advanced Model Structure

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'task.freezed.dart';
part 'task.g.dart';

@freezed
class Task with _$Task {
  const factory Task({
    required String id,
    required String title,
    required String description,
    @Default(false) bool isCompleted,
    required DateTime createdAt,
    DateTime? completedAt,
  }) = _Task;

  const Task._(); // For custom methods

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);

  // Custom methods
  bool get isOverdue => !isCompleted && DateTime.now().isAfter(createdAt.add(Duration(days: 7)));

  Task markCompleted() => copyWith(
    isCompleted: true,
    completedAt: DateTime.now(),
  );

  Task markUncompleted() => copyWith(
    isCompleted: false,
    completedAt: null,
  );
}
```

## 🧭 Go Router Architecture

### Route Constants Structure

```dart
// shared/constants/app_routes.dart
abstract class AppRoutePath {
  static const String home = '/';
  static const String tasks = '/tasks';
  static const String addTask = '/add-task';
  static const String editTask = '/edit-task/:id';
  static const String profile = '/profile';
}

abstract class AppRouteName {
  static const String home = 'home';
  static const String tasks = 'tasks';
  static const String addTask = 'addTask';
  static const String editTask = 'editTask';
  static const String profile = 'profile';
}
```

### Feature Routes Example

```dart
// features/_example/example_routes.dart
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';

final exampleRoutes = [
  GoRoute(
    path: AppRoutePath.tasks,
    name: AppRouteName.tasks,
    builder: (context, state) => const TaskListScreen(),
  ),
  GoRoute(
    path: AppRoutePath.addTask,
    name: AppRouteName.addTask,
    builder: (context, state) => const AddTaskScreen(),
  ),
  GoRoute(
    path: AppRoutePath.editTask,
    name: AppRouteName.editTask,
    builder: (context, state) {
      final taskId = state.pathParameters['id']!;
      final task = state.extra as Task?;
      return EditTaskScreen(taskId: taskId, initialTask: task);
    },
  ),
];
```

### Central Router Configuration

```dart
// shared/routing/app_router.dart
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutePath.home,
    routes: [
      ...exampleRoutes,
      ...authRoutes,
      // Future: ShellRoute for bottom navigation
    ],
    errorBuilder: (context, state) => ErrorScreen(error: state.error),
  );
});
```

## 🛠 Common Utils Detail

### Available Utilities

```dart
// shared/utils/common_utils.dart

// Date & Time
DateUtils.formatDate(DateTime.now()); // '29/09/2025'
DateUtils.formatTime(DateTime.now()); // '14:30'
DateUtils.isSameDay(date1, date2); // bool
DateUtils.timeAgo(DateTime.now().subtract(Duration(hours: 2))); // '2 hours ago'

// String
StringUtils.isNotNullOrEmpty(str); // bool
StringUtils.capitalize('hello'); // 'Hello'
StringUtils.truncate('long text here', 10); // 'long text...'
StringUtils.removeHtmlTags('<p>Hello</p>'); // 'Hello'

// Validation
ValidationUtils.isValidEmail(email); // bool
ValidationUtils.validateRequired(value, 'Name'); // String?
ValidationUtils.validateEmail(email); // String?
ValidationUtils.validateMinLength(value, 6, 'Password'); // String?

// Number
NumberUtils.formatCurrency(1234.56); // '฿1,234.56'
NumberUtils.formatNumber(1500000); // '1.5M'
NumberUtils.parseDouble(str); // double?
```

## 🔄 Advanced State Management Patterns

### Complete Feature Integration Example

```dart
// Complete feature provider implementation
class TaskProvider extends StateNotifier<List<Task>> {
  TaskProvider(this._ref) : super([]);

  final Ref _ref;

  Future<void> loadTasks() async {
    try {
      // 1. Start loading with specific key
      _ref.read(loadingProvider.notifier).startLoading('tasks');

      // 2. Clear any previous errors
      _ref.read(errorProvider.notifier).clearError();

      // 3. Use global API service with Freezed models
      final api = _ref.read(apiProvider);
      final tasks = await api.getList('/tasks', Task.fromJson);

      // 4. Update immutable state
      state = tasks;

      // 5. Optional success feedback
      ScaffoldMessenger.of(_ref.read(navigatorKeyProvider).currentContext!)
          .showSnackBar(const SnackBar(content: Text('Tasks loaded successfully!')));

    } on ApiException catch (e) {
      // 6. Handle specific API errors
      _ref.read(errorProvider.notifier).handleApiError(e, context: 'loadTasks');

    } catch (e) {
      // 7. Handle unexpected errors
      _ref.read(errorProvider.notifier).handleError('Unexpected error: $e');

    } finally {
      // 8. Always stop loading
      _ref.read(loadingProvider.notifier).stopLoading('tasks');
    }
  }

  // Optimistic updates with rollback on failure
  Future<void> toggleTask(String taskId) async {
    final taskIndex = state.indexWhere((task) => task.id == taskId);
    if (taskIndex == -1) return;

    final currentTask = state[taskIndex];

    // Use Freezed copyWith for immutable updates
    final updatedTask = currentTask.isCompleted
        ? currentTask.markUncompleted()  // Custom Freezed method
        : currentTask.markCompleted();   // Custom Freezed method

    // Update local state immediately (optimistic update)
    final updatedTasks = [...state];
    updatedTasks[taskIndex] = updatedTask;
    state = updatedTasks;

    try {
      // Sync with server
      final api = _ref.read(apiProvider);
      await api.update('/tasks', taskId, updatedTask.toJson(), Task.fromJson);
    } catch (e) {
      // Rollback on error
      updatedTasks[taskIndex] = currentTask;
      state = [...updatedTasks];

      _ref.read(errorProvider.notifier).handleError('Failed to update task');
    }
  }

  Future<void> addTask(Task task) async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('addTask');

      final api = _ref.read(apiProvider);
      final newTask = await api.create('/tasks', task.toJson(), Task.fromJson);

      // Add to existing state immutably
      state = [...state, newTask];

    } on ApiException catch (e) {
      _ref.read(errorProvider.notifier).handleApiError(e, context: 'addTask');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('addTask');
    }
  }

  Future<void> deleteTask(String taskId) async {
    final taskIndex = state.indexWhere((task) => task.id == taskId);
    if (taskIndex == -1) return;

    final taskToDelete = state[taskIndex];

    // Optimistic delete
    state = state.where((task) => task.id != taskId).toList();

    try {
      final api = _ref.read(apiProvider);
      await api.delete('/tasks', taskId);
    } catch (e) {
      // Restore on error
      final restoredTasks = [...state];
      restoredTasks.insert(taskIndex, taskToDelete);
      state = restoredTasks;

      _ref.read(errorProvider.notifier).handleError('Failed to delete task');
    }
  }
}

// Provider definition with proper typing
final taskProvider = StateNotifierProvider<TaskProvider, List<Task>>((ref) {
  return TaskProvider(ref);
});

// Computed providers for derived state
final completedTasksProvider = Provider<List<Task>>((ref) {
  final tasks = ref.watch(taskProvider);
  return tasks.where((task) => task.isCompleted).toList();
});

final pendingTasksProvider = Provider<List<Task>>((ref) {
  final tasks = ref.watch(taskProvider);
  return tasks.where((task) => !task.isCompleted).toList();
});

final taskStatsProvider = Provider<TaskStats>((ref) {
  final tasks = ref.watch(taskProvider);
  final completed = tasks.where((task) => task.isCompleted).length;
  final total = tasks.length;

  return TaskStats(
    total: total,
    completed: completed,
    pending: total - completed,
    completionRate: total > 0 ? completed / total : 0.0,
  );
});
```

### Advanced UI Integration

```dart
class TaskListScreen extends ConsumerWidget {
  const TaskListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch multiple providers
    final tasks = ref.watch(taskProvider);
    final isLoading = ref.watch(isLoadingProvider('tasks'));
    final isAddingTask = ref.watch(isLoadingProvider('addTask'));
    final currentError = ref.watch(errorProvider);
    final taskStats = ref.watch(taskStatsProvider);

    // Listen for one-time events
    ref.listen<AppError?>(errorProvider, (previous, next) {
      if (next != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.message),
            backgroundColor: Colors.red,
            action: SnackBarAction(
              label: 'Dismiss',
              onPressed: () => ref.read(errorProvider.notifier).clearError(),
            ),
          ),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tasks'),
        actions: [
          // Theme toggle
          IconButton(
            icon: Icon(
              ref.watch(themeModeProvider) == ThemeMode.light
                  ? Icons.dark_mode
                  : Icons.light_mode,
            ),
            onPressed: () => ref.read(themeModeProvider.notifier).toggleTheme(),
          ),
          // Refresh action
          if (!isLoading)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => ref.read(taskProvider.notifier).loadTasks(),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(taskProvider.notifier).loadTasks(),
        child: Column(
          children: [
            // Stats card
            Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _StatItem('Total', taskStats.total.toString()),
                    _StatItem('Completed', taskStats.completed.toString()),
                    _StatItem('Pending', taskStats.pending.toString()),
                    _StatItem(
                      'Progress',
                      '${(taskStats.completionRate * 100).toInt()}%',
                    ),
                  ],
                ),
              ),
            ),

            // Error display
            if (currentError != null)
              Container(
                width: double.infinity,
                color: Colors.red.shade100,
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 8),
                    Expanded(child: Text(currentError.message)),
                    TextButton(
                      onPressed: () => ref.read(errorProvider.notifier).clearError(),
                      child: const Text('Dismiss'),
                    ),
                  ],
                ),
              ),

            // Loading indicator
            if (isLoading)
              const LinearProgressIndicator(),

            // Content
            Expanded(
              child: tasks.isEmpty && !isLoading
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.task_alt, size: 64, color: Colors.grey),
                          SizedBox(height: 16),
                          Text(
                            'No tasks yet',
                            style: TextStyle(fontSize: 18, color: Colors.grey),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Tap + to add your first task',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: tasks.length,
                      itemBuilder: (context, index) {
                        final task = tasks[index];
                        return TaskTile(
                          task: task,
                          onToggle: () => ref
                              .read(taskProvider.notifier)
                              .toggleTask(task.id),
                          onEdit: () => context.pushNamed(
                            AppRouteName.editTask,
                            pathParameters: {'id': task.id},
                            extra: task,
                          ),
                          onDelete: () => _showDeleteDialog(context, ref, task),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: isAddingTask
            ? null
            : () => context.pushNamed(AppRouteName.addTask),
        child: isAddingTask
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.add),
      ),
    );
  }

  void _showDeleteDialog(BuildContext context, WidgetRef ref, Task task) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Task'),
        content: Text('Are you sure you want to delete "${task.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              ref.read(taskProvider.notifier).deleteTask(task.id);
            },
            child: const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;

  const _StatItem(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class TaskTile extends StatelessWidget {
  final Task task;
  final VoidCallback onToggle;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const TaskTile({
    super.key,
    required this.task,
    required this.onToggle,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: Checkbox(
          value: task.isCompleted,
          onChanged: (_) => onToggle(),
        ),
        title: Text(
          task.title,
          style: TextStyle(
            decoration: task.isCompleted
                ? TextDecoration.lineThrough
                : TextDecoration.none,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (task.description.isNotEmpty)
              Text(
                task.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            const SizedBox(height: 4),
            Text(
              'Created: ${DateUtils.formatDate(task.createdAt)}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (task.completedAt != null)
              Text(
                'Completed: ${DateUtils.formatDate(task.completedAt!)}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
          ],
        ),
        trailing: PopupMenuButton(
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'edit',
              child: Row(
                children: [
                  Icon(Icons.edit),
                  SizedBox(width: 8),
                  Text('Edit'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'delete',
              child: Row(
                children: [
                  Icon(Icons.delete, color: Colors.red),
                  SizedBox(width: 8),
                  Text('Delete', style: TextStyle(color: Colors.red)),
                ],
              ),
            ),
          ],
          onSelected: (value) {
            switch (value) {
              case 'edit':
                onEdit();
                break;
              case 'delete':
                onDelete();
                break;
            }
          },
        ),
        onTap: onEdit,
      ),
    );
  }
}
```

## 📱 Advanced Main App Configuration

### Complete Setup with Error Boundary

```dart
// main.dart - Production-ready setup
class MainApp extends ConsumerStatefulWidget {
  @override
  ConsumerState<MainApp> createState() => _MainAppState();
}

class _MainAppState extends ConsumerState<MainApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // Initialize app on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeApp();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        // App came to foreground
        _handleAppResumed();
        break;
      case AppLifecycleState.paused:
        // App went to background
        _handleAppPaused();
        break;
      case AppLifecycleState.detached:
        // App is closing
        _handleAppDetached();
        break;
      default:
        break;
    }
  }

  void _initializeApp() {
    // Initialize global providers
    ref.read(themeProvider.notifier).loadSavedTheme();
    ref.read(authProvider.notifier).checkAuthStatus();
  }

  void _handleAppResumed() {
    // Refresh data when app resumes
    ref.read(authProvider.notifier).refreshTokenIfNeeded();
  }

  void _handleAppPaused() {
    // Save state when app goes to background
    ref.read(themeProvider.notifier).saveCurrentTheme();
  }

  void _handleAppDetached() {
    // Cleanup before app closes
    ref.read(apiProvider).cancelAllRequests();
  }

  @override
  Widget build(BuildContext context) {
    // Watch global providers
    final themeMode = ref.watch(themeModeProvider);
    final lightTheme = ref.watch(lightThemeProvider);
    final darkTheme = ref.watch(darkThemeProvider);
    final router = ref.watch(appRouterProvider);

    // Listen for global errors
    ref.listen<AppError?>(errorProvider, (previous, next) {
      if (next != null && next.shouldShowGlobally) {
        _showGlobalError(next);
      }
    });

    return MaterialApp.router(
      title: AppConfig.appName,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: themeMode,
      routerConfig: router,

      // Global error boundary
      builder: (context, child) {
        return GlobalErrorBoundary(
          child: LoadingOverlay(
            child: child ?? const SizedBox(),
          ),
        );
      },

      // Debug settings
      debugShowCheckedModeBanner: false,

      // Localization support
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en', 'US'),
        Locale('th', 'TH'),
      ],
    );
  }

  void _showGlobalError(AppError error) {
    // Show global error dialog or snackbar
    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text(error.message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                ref.read(errorProvider.notifier).clearError();
              },
              child: const Text('OK'),
            ),
            if (error.isRetryable)
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  error.retryCallback?.call();
                },
                child: const Text('Retry'),
              ),
          ],
        ),
      );
    }
  }
}

// Global error boundary widget
class GlobalErrorBoundary extends StatelessWidget {
  final Widget child;

  const GlobalErrorBoundary({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return ErrorBoundary(
      onError: (error, stackTrace) {
        // Log error to crash reporting service
        FirebaseCrashlytics.instance.recordError(error, stackTrace);

        // Show error UI
        return const MaterialApp(
          home: ErrorScreen(
            title: 'Something went wrong',
            message: 'The app encountered an unexpected error. Please restart the app.',
          ),
        );
      },
      child: child,
    );
  }
}

// Global loading overlay
class LoadingOverlay extends ConsumerWidget {
  final Widget child;

  const LoadingOverlay({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final hasGlobalLoading = ref.watch(hasAnyLoadingProvider);

    return Stack(
      children: [
        child,
        if (hasGlobalLoading)
          Container(
            color: Colors.black26,
            child: const Center(
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Loading...'),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
```

## 🎨 Advanced Patterns & Best Practices

### 1. **Provider Organization**

```dart
// Feature-specific provider grouping
class TaskProviders {
  static final list = StateNotifierProvider<TaskListNotifier, List<Task>>((ref) {
    return TaskListNotifier(ref);
  });

  static final search = StateNotifierProvider<TaskSearchNotifier, TaskSearchState>((ref) {
    return TaskSearchNotifier(ref);
  });

  static final filter = StateNotifierProvider<TaskFilterNotifier, TaskFilter>((ref) {
    return TaskFilterNotifier(ref);
  });

  // Computed providers
  static final filteredTasks = Provider<List<Task>>((ref) {
    final tasks = ref.watch(list);
    final filter = ref.watch(TaskProviders.filter);
    final searchQuery = ref.watch(search).query;

    return tasks
        .where((task) => filter.applies(task))
        .where((task) => searchQuery.isEmpty || task.title.toLowerCase().contains(searchQuery.toLowerCase()))
        .toList();
  });

  static final statistics = Provider<TaskStatistics>((ref) {
    final tasks = ref.watch(list);
    return TaskStatistics.fromTasks(tasks);
  });
}
```

### 2. **Error Handling Hierarchy**

```dart
// Custom exception hierarchy
abstract class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppException(
    this.message, {
    this.code,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() => 'AppException: $message';
}

class ApiException extends AppException {
  final int? statusCode;
  final Map<String, dynamic>? response;

  const ApiException(
    super.message, {
    super.code,
    super.originalError,
    super.stackTrace,
    this.statusCode,
    this.response,
  });

  bool get isNetworkError => statusCode == null;
  bool get isServerError => statusCode != null && statusCode! >= 500;
  bool get isClientError => statusCode != null && statusCode! >= 400 && statusCode! < 500;
  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
}

class ValidationException extends AppException {
  final Map<String, List<String>> fieldErrors;

  const ValidationException(
    super.message, {
    super.code,
    super.originalError,
    super.stackTrace,
    this.fieldErrors = const {},
  });
}

class NetworkException extends AppException {
  const NetworkException(super.message, {
    super.code,
    super.originalError,
    super.stackTrace,
  });
}

// Global error handler
class ErrorNotifier extends StateNotifier<AppError?> {
  ErrorNotifier() : super(null);

  void handleException(Exception exception, {String? context}) {
    final error = _mapExceptionToError(exception, context);
    state = error;

    // Log to analytics/crash reporting
    _logError(error);
  }

  AppError _mapExceptionToError(Exception exception, String? context) {
    switch (exception.runtimeType) {
      case ApiException:
        final apiEx = exception as ApiException;
        return AppError.api(
          message: apiEx.message,
          statusCode: apiEx.statusCode,
          context: context,
          isRetryable: apiEx.isNetworkError || apiEx.isServerError,
        );

      case ValidationException:
        final validationEx = exception as ValidationException;
        return AppError.validation(
          message: validationEx.message,
          fieldErrors: validationEx.fieldErrors,
          context: context,
        );

      case NetworkException:
        return AppError.network(
          message: 'Network connection failed',
          context: context,
          isRetryable: true,
        );

      default:
        return AppError.unknown(
          message: exception.toString(),
          context: context,
        );
    }
  }

  void _logError(AppError error) {
    // Send to crash reporting service
    FirebaseCrashlytics.instance.recordError(
      error.message,
      null,
      information: [
        'Context: ${error.context}',
        'Type: ${error.type}',
        'Is Retryable: ${error.isRetryable}',
      ],
    );

    // Log for debugging
    developer.log(
      'Error occurred: ${error.message}',
      name: 'ErrorHandler',
      error: error,
      level: error.type == ErrorType.validation ? 400 : 1000,
    );
  }
}
```

### 3. **Performance Optimization**

```dart
// Optimized list rendering with keys and memoization
class OptimizedTaskList extends ConsumerWidget {
  const OptimizedTaskList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasks = ref.watch(TaskProviders.filteredTasks);

    return ListView.builder(
      // Performance optimizations
      itemExtent: 80, // Fixed height for better performance
      cacheExtent: 1000, // Cache more items
      itemCount: tasks.length,
      itemBuilder: (context, index) {
        final task = tasks[index];

        // Use stable keys for efficient rebuilds
        return TaskItem(
          key: ValueKey(task.id),
          task: task,
        );
      },
    );
  }
}

// Memoized widget to prevent unnecessary rebuilds
class TaskItem extends ConsumerWidget {
  final Task task;

  const TaskItem({super.key, required this.task});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Only rebuild when this specific task changes
    return Card(
      key: ValueKey(task.id),
      child: ListTile(
        leading: Checkbox(
          value: task.isCompleted,
          onChanged: (_) => ref.read(TaskProviders.list.notifier).toggle(task.id),
        ),
        title: Text(task.title),
        subtitle: Text(
          DateUtils.formatRelativeTime(task.createdAt),
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: _buildTrailing(context, ref),
      ),
    );
  }

  Widget _buildTrailing(BuildContext context, WidgetRef ref) {
    // Memoize expensive computations
    return useMemoized(
      () => PopupMenuButton<String>(
        onSelected: (value) => _handleMenuAction(value, ref),
        itemBuilder: (context) => [
          const PopupMenuItem(value: 'edit', child: Text('Edit')),
          const PopupMenuItem(value: 'delete', child: Text('Delete')),
        ],
      ),
      [task.id], // Only rebuild when task ID changes
    );
  }

  void _handleMenuAction(String action, WidgetRef ref) {
    switch (action) {
      case 'edit':
        context.pushNamed('/tasks/edit/${task.id}', extra: task);
        break;
      case 'delete':
        ref.read(TaskProviders.list.notifier).delete(task.id);
        break;
    }
  }
}

// State preservation for complex forms
class FormStateManager<T> extends StateNotifier<FormState<T>> {
  FormStateManager(T initialData) : super(FormState.initial(initialData));

  void updateField(String field, dynamic value) {
    state = state.copyWith(
      data: state.data.copyWith({field: value}),
      isDirty: true,
      errors: {...state.errors}..remove(field),
    );
  }

  void setErrors(Map<String, String> errors) {
    state = state.copyWith(errors: errors);
  }

  void setLoading(bool loading) {
    state = state.copyWith(isLoading: loading);
  }

  bool validate() {
    final errors = <String, String>{};

    // Add validation logic here

    setErrors(errors);
    return errors.isEmpty;
  }
}
```

### 4. **Testing Patterns**

```dart
// Provider testing utilities
class TestProviders {
  static ProviderContainer createContainer({
    List<Override> overrides = const [],
  }) {
    return ProviderContainer(
      overrides: [
        // Mock global services
        apiProvider.overrideWithValue(MockApiService()),
        storageProvider.overrideWithValue(MockStorage()),
        ...overrides,
      ],
    );
  }

  static Future<void> pumpWithProviders(
    WidgetTester tester,
    Widget widget, {
    List<Override> overrides = const [],
  }) async {
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: createContainer(overrides: overrides),
        child: MaterialApp(home: widget),
      ),
    );
  }
}

// Example test
void main() {
  group('TaskProvider', () {
    testWidgets('loads tasks successfully', (tester) async {
      final mockApi = MockApiService();
      when(() => mockApi.getList('/tasks', any()))
          .thenAnswer((_) async => [
            const Task(id: '1', title: 'Test Task', createdAt: ...),
          ]);

      await TestProviders.pumpWithProviders(
        tester,
        const TaskListScreen(),
        overrides: [
          apiProvider.overrideWithValue(mockApi),
        ],
      );

      // Wait for loading to complete
      await tester.pumpAndSettle();

      // Verify UI
      expect(find.text('Test Task'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    test('handles API errors correctly', () async {
      final container = TestProviders.createContainer(
        overrides: [
          apiProvider.overrideWithValue(MockApiService()
            ..when(() => mockApi.getList('/tasks', any()))
              .thenThrow(const ApiException('Network error'))),
        ],
      );

      final notifier = container.read(TaskProviders.list.notifier);
      await notifier.loadTasks();

      final error = container.read(errorProvider);
      expect(error, isNotNull);
      expect(error!.message, contains('Network error'));
    });
  });
}
```
