import 'package:hourz/shared/models/api.dart';
import 'package:hourz/shared/providers/index.dart';

import 'package:hourz/shared/services/api_service.dart';
import '../models/auth.dart';

class AuthService {
  final ApiService _apiService;
  static const String _loginEndpoint = '/auth/login';
  static const String _registerEndpoint = '/auth/register';
  static const String _logoutEndpoint = '/auth/logout';
  static const String _refreshEndpoint = '/auth/refresh';

  AuthService(this._apiService);

  Future<LoginResponse> login(LoginRequest request) async {
    return await _apiService.postForm(
      _loginEndpoint,
      request.toFormData(),
      LoginResponse.fromJson,
    );
  }

  Future<CreateResponse> register(RegisterRequest request) async {
    return await _apiService.create(_registerEndpoint, request.toJson());
  }

  Future<void> logout() async {
    await _apiService.delete(_logoutEndpoint, '');
  }

  Future<RefreshTokenResponse> refreshToken(
    String refreshToken,
    String oldAccessToken,
  ) async {
    // Set the refresh token as the Authorization header
    _apiService.setAuthToken(refreshToken);

    try {
      final response = await _apiService.create(
        _refreshEndpoint,
        {}, // Empty body as per API spec
        RefreshTokenResponse.fromJson,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> loginWithGoogle() async {
    // TODO: Implement Google OAuth
    throw UnimplementedError('Google login not implemented yet');
  }
}
