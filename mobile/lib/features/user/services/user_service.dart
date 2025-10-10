import 'package:hourz/shared/providers/index.dart';

import '../models/user.dart';

class UserService {
  final ApiService _apiService;

  UserService(this._apiService);

  Future<User> getCurrentUser() async {
    return await _apiService.get(ApiEndpoints.login, User.fromJson);
  }
}
