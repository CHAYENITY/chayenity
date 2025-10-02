import 'package:hourz/shared/providers/index.dart';
import '../models/user.dart';

class AuthService {
  final ApiService _apiService;
  static const String _loginEndpoint = '/auth/login';
  static const String _registerEndpoint = '/auth/register';
  static const String _logoutEndpoint = '/auth/logout';
  static const String _refreshEndpoint = '/auth/refresh';
  static const String _meEndpoint = '/users/me';

  AuthService(this._apiService);

  Future<LoginResponse> login(LoginRequest request) async {
    print('🔵 [AUTH_SERVICE] Logging in with: ${request.email}');
    return await _apiService.postForm(
      _loginEndpoint,
      request.toFormData(),
      LoginResponse.fromJson,
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
    print('🔵 [AUTH_SERVICE] Fetching current user from: $_meEndpoint');
    return await _apiService.get(_meEndpoint, User.fromJson);
  }

  Future<RefreshTokenResponse> refreshToken(
    String refreshToken,
    String oldAccessToken,
  ) async {
    print('🔵 [AUTH_SERVICE] Refreshing access token');

    // Set the refresh token as the Authorization header
    _apiService.setAuthToken(refreshToken);

    try {
      final response = await _apiService.create(
        _refreshEndpoint,
        {}, // Empty body as per API spec
        RefreshTokenResponse.fromJson,
      );
      print('🟢 [AUTH_SERVICE] Token refresh successful');
      return response;
    } catch (e) {
      print('🔴 [AUTH_SERVICE] Token refresh failed: $e');
      rethrow;
    }
  }

  Future<void> loginWithGoogle() async {
    // TODO: Implement Google OAuth
    throw UnimplementedError('Google login not implemented yet');
  }
}
