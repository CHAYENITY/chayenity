import '../models/login_request.dart';
import '../models/login_response.dart';
import '../../../shared/services/index.dart';

abstract class AuthRepository {
  Future<LoginResponse> login(LoginRequest request);
  Future<void> logout();
  Future<LoginResponse> refreshToken(String refreshToken);
  Future<bool> isTokenValid(String token);
}

class AuthRepositoryImpl implements AuthRepository {
  final HttpService _http;

  AuthRepositoryImpl({HttpService? httpService})
    : _http = httpService ?? HttpService.instance;

  @override
  Future<LoginResponse> login(LoginRequest request) async {
    try {
      // 🔥 Super simple API call
      final data = await _http.post<Map<String, dynamic>>(
        ApiEndpoints.login,
        data: request.toJson(),
      );
      return LoginResponse.fromJson(data);
    } on HttpException catch (e) {
      throw AuthException(e.message);
    } catch (e) {
      throw const AuthException('Login failed. Please try again.');
    }
  }

  @override
  Future<void> logout() async {
    try {
      await _http.post(ApiEndpoints.logout);
    } catch (e) {
      // Silent fail - clear local state anyway
    }
  }

  @override
  Future<LoginResponse> refreshToken(String refreshToken) async {
    try {
      final data = await _http.post<Map<String, dynamic>>(
        ApiEndpoints.refreshToken,
        data: {'refresh_token': refreshToken},
      );
      return LoginResponse.fromJson(data);
    } on HttpException catch (e) {
      throw AuthException(e.message);
    } catch (e) {
      throw const AuthException('Token refresh failed. Please login again.');
    }
  }

  @override
  Future<bool> isTokenValid(String token) async {
    try {
      await _http.get(ApiEndpoints.currentUser);
      return true;
    } catch (e) {
      return false;
    }
  }
}

class AuthException implements Exception {
  final String message;
  const AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}
