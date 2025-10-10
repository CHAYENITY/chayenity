import 'package:freezed_annotation/freezed_annotation.dart';

part 'token_model.freezed.dart';
part 'token_model.g.dart';

/// Token storage model with expiry tracking
@freezed
class TokenModel with _$TokenModel {
  const factory TokenModel({
    required String accessToken,
    required String refreshToken,
    required DateTime accessTokenExpiry,
    required DateTime refreshTokenExpiry,
    @Default('bearer') String tokenType,
  }) = _TokenModel;

  const TokenModel._();

  factory TokenModel.fromJson(Map<String, dynamic> json) =>
      _$TokenModelFromJson(json);

  /// Create from login response
  factory TokenModel.fromLoginResponse({
    required String accessToken,
    required String refreshToken,
    String tokenType = 'bearer',
    Duration accessTokenDuration = const Duration(minutes: 10),
    Duration refreshTokenDuration = const Duration(days: 7),
  }) {
    final now = DateTime.now();
    return TokenModel(
      accessToken: accessToken,
      refreshToken: refreshToken,
      tokenType: tokenType,
      accessTokenExpiry: now.add(accessTokenDuration),
      refreshTokenExpiry: now.add(refreshTokenDuration),
    );
  }

  /// Update only access token (after refresh)
  TokenModel copyWithNewAccessToken(String newAccessToken) {
    return copyWith(
      accessToken: newAccessToken,
      accessTokenExpiry: DateTime.now().add(const Duration(minutes: 10)),
    );
  }

  /// Check if access token is expired or will expire soon (within 1 minute)
  bool get isAccessTokenExpired {
    return DateTime.now().isAfter(
      accessTokenExpiry.subtract(const Duration(minutes: 1)),
    );
  }

  /// Check if refresh token is expired
  bool get isRefreshTokenExpired {
    return DateTime.now().isAfter(refreshTokenExpiry);
  }

  /// Check if token is still valid
  bool get isValid => !isRefreshTokenExpired;

  /// Get authorization header value
  String get authHeader => '$tokenType $accessToken';

  /// Get refresh authorization header value
  String get refreshAuthHeader => '$tokenType $refreshToken';
}
