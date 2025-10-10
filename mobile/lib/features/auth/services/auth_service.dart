import 'package:hourz/shared/models/api.dart';

import 'package:hourz/shared/providers/index.dart';

import '../models/auth.dart';

class AuthService {
  final ApiService _apiService;

  AuthService(this._apiService);

  Future<CreateResponse> register(RegisterRequest request) async {
    return await _apiService.create(
      ApiEndpoints.register,
      request.toJson(),
      CreateResponse.fromJson,
    );
  }

  Future<TokenModel> login(LoginRequest request) async {
    final response = await _apiService.postForm(
      ApiEndpoints.login,
      request.toFormData(),
      LoginResponse.fromJson,
    );

    // Convert LoginResponse to TokenModel with expiry tracking
    return TokenModel.fromLoginResponse(
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      tokenType: response.tokenType,
    );
  }

  Future<String> refreshToken(String refreshToken) async {
    final response = await _apiService.postForm(
      ApiEndpoints.refreshToken,
      {},
      RefreshTokenResponse.fromJson,
    );
    return response.accessToken;
  }

  Future<void> logout() async {
    await _apiService.delete(ApiEndpoints.logout, '');
  }
}
