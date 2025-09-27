import '../../auth/models/user_model.dart';
import '../../../shared/services/index.dart';

/// 👤 User Repository - ใช้ global HttpService
class UserRepository {
  final HttpService _http = HttpService.instance;

  // 🔥 Super simple CRUD operations

  Future<User> getCurrentUser() async {
    try {
      final data = await _http.get<Map<String, dynamic>>(
        ApiEndpoints.currentUser,
      );
      return User.fromJson(data);
    } on HttpException catch (e) {
      throw UserException(e.message);
    }
  }

  Future<User> updateProfile(User profile) async {
    try {
      final data = await _http.put<Map<String, dynamic>>(
        ApiEndpoints.updateProfile,
        data: profile.toJson(),
      );
      return User.fromJson(data);
    } on HttpException catch (e) {
      throw UserException(e.message);
    }
  }

  Future<List<User>> getUsers({int page = 1, int limit = 20}) async {
    try {
      final data = await _http.get<Map<String, dynamic>>(
        ApiEndpoints.users,
        params: {'page': page, 'limit': limit},
      );

      final users = (data['users'] as List)
          .map((json) => User.fromJson(json))
          .toList();

      return users;
    } on HttpException catch (e) {
      throw UserException(e.message);
    }
  }

  Future<void> deleteUser(String userId) async {
    try {
      await _http.delete('${ApiEndpoints.users}/$userId');
    } on HttpException catch (e) {
      throw UserException(e.message);
    }
  }
}

class UserException implements Exception {
  final String message;
  const UserException(this.message);

  @override
  String toString() => 'UserException: $message';
}
