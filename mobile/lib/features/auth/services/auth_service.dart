import 'package:hourz/shared/providers/index.dart';
import '../models/user.dart';

class AuthService {
  final ApiService _apiService;
  static const String _loginEndpoint = '/auth/login';
  static const String _registerEndpoint = '/auth/register';
  static const String _logoutEndpoint = '/auth/logout';
  static const String _meEndpoint = '/auth/me';

  AuthService(this._apiService);

  Future<User> login(LoginRequest request) async {
    return await _apiService.create(
      _loginEndpoint,
      request.toJson(),
      User.fromJson,
    );
  }

  Future<User> register(RegisterRequest request) async {
    return await _apiService.create(
      _registerEndpoint,
      request.toJson(),
      User.fromJson,
    );
  }

  Future<void> logout() async {
    await _apiService.delete(_logoutEndpoint, '');
  }

  Future<User> getCurrentUser() async {
    return await _apiService.getById(_meEndpoint, '', User.fromJson);
  }

  Future<void> loginWithGoogle() async {
    // TODO: Implement Google OAuth
    throw UnimplementedError('Google login not implemented yet');
  }
}
