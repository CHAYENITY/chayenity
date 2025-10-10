import 'package:freezed_annotation/freezed_annotation.dart';

part 'example.freezed.dart';
part 'example.g.dart';

// * Task Model - CRUD operations
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

  const Task._();

  // * Create Task from JSON (API Response)
  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);

  // * Create Task for API requests (without id and timestamps)
  Map<String, dynamic> toCreateJson() {
    return {
      'title': title,
      'description': description,
      'is_completed': isCompleted,
    };
  }

  // * Create Task for update requests
  Map<String, dynamic> toUpdateJson() {
    return {
      'title': title,
      'description': description,
      'is_completed': isCompleted,
    };
  }

  // * Mark task as completed
  Task markCompleted() {
    return copyWith(isCompleted: true, completedAt: DateTime.now());
  }

  // * Mark task as uncompleted
  Task markUncompleted() {
    return copyWith(isCompleted: false, completedAt: null);
  }
}
