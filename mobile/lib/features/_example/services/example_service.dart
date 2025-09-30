import 'package:hourz/shared/providers/index.dart';
import '../models/example.dart';

/// Task Service - จัดการ API calls เฉพาะ Task feature
class TaskService {
  final ApiService _apiService;
  static const String _endpoint = '/tasks';

  TaskService(this._apiService);

  /// GET - ดึงรายการ tasks ทั้งหมด
  Future<List<Task>> getTasks() async {
    return await _apiService.getList(_endpoint, Task.fromJson);
  }

  /// GET - ดึง task ตาม ID
  Future<Task> getTaskById(String id) async {
    return await _apiService.getById(_endpoint, id, Task.fromJson);
  }

  /// POST - สร้าง task ใหม่
  Future<Task> createTask(Task task) async {
    return await _apiService.create(
      _endpoint,
      task.toCreateJson(),
      Task.fromJson,
    );
  }

  /// PUT - อัปเดต task
  Future<Task> updateTask(Task task) async {
    return await _apiService.update(
      _endpoint,
      task.id,
      task.toUpdateJson(),
      Task.fromJson,
    );
  }

  /// DELETE - ลบ task
  Future<void> deleteTask(String id) async {
    await _apiService.delete(_endpoint, id);
  }

  /// PATCH - Toggle task completion (custom endpoint)
  Future<Task> toggleTaskCompletion(String id) async {
    // สำหรับ custom API endpoint
    final response = await _apiService.update(
      '$_endpoint/$id/toggle',
      id,
      {}, // Empty body for toggle action
      Task.fromJson,
    );
    return response;
  }

  /// GET - ดึง completed tasks เฉพาะ
  Future<List<Task>> getCompletedTasks() async {
    return await _apiService.getList(
      '$_endpoint?completed=true',
      Task.fromJson,
    );
  }

  /// GET - ดึง pending tasks เฉพาะ
  Future<List<Task>> getPendingTasks() async {
    return await _apiService.getList(
      '$_endpoint?completed=false',
      Task.fromJson,
    );
  }
}
