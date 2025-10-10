import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/models/token_model.dart';
import 'package:hourz/shared/services/secure_storage_service.dart';
import 'package:logger/logger.dart';

/// Provider for SecureStorageService
final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

/// Provider for current token (in-memory cache)
final tokenProvider = StateNotifierProvider<TokenNotifier, TokenModel?>((ref) {
  return TokenNotifier(ref);
});

/// Token state manager
class TokenNotifier extends StateNotifier<TokenModel?> {
  final Ref _ref;
  final Logger _logger = Logger();

  TokenNotifier(this._ref) : super(null);

  /// Load token from secure storage on app start
  Future<void> loadToken() async {
    try {
      final storage = _ref.read(secureStorageProvider);
      final token = await storage.getToken();

      if (token != null && !token.isRefreshTokenExpired) {
        state = token;
        _logger.d('✅ Token loaded from storage');
      } else {
        state = null;
        _logger.d('❌ No valid token found');
      }
    } catch (e) {
      _logger.e('❌ Failed to load token: $e');
      state = null;
    }
  }

  /// Save token (after login or refresh)
  Future<void> saveToken(TokenModel token) async {
    try {
      final storage = _ref.read(secureStorageProvider);
      await storage.saveToken(token);
      state = token;
      _logger.d('✅ Token saved');
    } catch (e) {
      _logger.e('❌ Failed to save token: $e');
      rethrow;
    }
  }

  /// Update access token (after refresh)
  Future<void> updateAccessToken(String newAccessToken) async {
    if (state == null) {
      _logger.w('⚠️ Cannot update access token: no token exists');
      return;
    }

    try {
      final newToken = state!.copyWithNewAccessToken(newAccessToken);
      await saveToken(newToken);
      _logger.d('✅ Access token updated');
    } catch (e) {
      _logger.e('❌ Failed to update access token: $e');
      rethrow;
    }
  }

  /// Clear token (logout)
  Future<void> clearToken() async {
    try {
      final storage = _ref.read(secureStorageProvider);
      await storage.deleteToken();
      state = null;
      _logger.d('✅ Token cleared');
    } catch (e) {
      _logger.e('❌ Failed to clear token: $e');
      rethrow;
    }
  }

  /// Check if user is authenticated
  bool get isAuthenticated => state != null && state!.isValid;

  /// Check if access token needs refresh
  bool get needsRefresh =>
      state != null &&
      state!.isAccessTokenExpired &&
      !state!.isRefreshTokenExpired;

  /// Get current access token
  String? get accessToken => state?.accessToken;

  /// Get current refresh token
  String? get refreshToken => state?.refreshToken;
}

/// Computed providers for convenience
final isAuthenticatedProvider = Provider<bool>((ref) {
  final token = ref.watch(tokenProvider);
  return token != null && token.isValid;
});

final needsRefreshProvider = Provider<bool>((ref) {
  final token = ref.watch(tokenProvider);
  return token != null &&
      token.isAccessTokenExpired &&
      !token.isRefreshTokenExpired;
});
