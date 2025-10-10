import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hourz/shared/models/token_model.dart';
import 'package:logger/logger.dart';

/// Service for secure token storage using FlutterSecureStorage
class SecureStorageService {
  final FlutterSecureStorage _storage;
  final Logger _logger = Logger();

  static const String _tokenKey = 'auth_token';

  SecureStorageService({FlutterSecureStorage? storage})
    : _storage =
          storage ??
          const FlutterSecureStorage(
            aOptions: AndroidOptions(encryptedSharedPreferences: true),
            iOptions: IOSOptions(
              accessibility: KeychainAccessibility.first_unlock,
            ),
          );

  /// Save token to secure storage
  Future<void> saveToken(TokenModel token) async {
    try {
      final jsonString = jsonEncode(token.toJson());
      await _storage.write(key: _tokenKey, value: jsonString);
      _logger.d('🔐 Token saved securely');
    } catch (e) {
      _logger.e('❌ Failed to save token: $e');
      rethrow;
    }
  }

  /// Get token from secure storage
  Future<TokenModel?> getToken() async {
    try {
      final jsonString = await _storage.read(key: _tokenKey);
      if (jsonString == null) {
        _logger.d('🔓 No token found');
        return null;
      }

      final jsonData = jsonDecode(jsonString) as Map<String, dynamic>;
      final token = TokenModel.fromJson(jsonData);

      // Check if token is still valid
      if (token.isRefreshTokenExpired) {
        _logger.w('⚠️ Refresh token expired, clearing storage');
        await deleteToken();
        return null;
      }

      _logger.d('🔐 Token retrieved successfully');
      return token;
    } catch (e) {
      _logger.e('❌ Failed to get token: $e');
      await deleteToken(); // Clear corrupted data
      return null;
    }
  }

  /// Delete token from secure storage
  Future<void> deleteToken() async {
    try {
      await _storage.delete(key: _tokenKey);
      _logger.d('🗑️ Token deleted');
    } catch (e) {
      _logger.e('❌ Failed to delete token: $e');
      rethrow;
    }
  }

  /// Clear all stored data
  Future<void> clearAll() async {
    try {
      await _storage.deleteAll();
      _logger.d('🗑️ All secure storage cleared');
    } catch (e) {
      _logger.e('❌ Failed to clear storage: $e');
      rethrow;
    }
  }

  /// Check if token exists
  Future<bool> hasToken() async {
    try {
      final token = await getToken();
      return token != null;
    } catch (e) {
      return false;
    }
  }
}
