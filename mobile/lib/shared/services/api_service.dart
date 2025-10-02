import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/models/api.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:logger/logger.dart';

/// Simple API Service for basic CRUD operations
class ApiService {
  late final Dio _dio;
  final Logger _logger = Logger();

  ApiService() {
    try {
      _dio = Dio(
        BaseOptions(
          baseUrl: ApiEndpoints.apiUrl,
          connectTimeout: AppConfig.apiTimeout,
          receiveTimeout: AppConfig.apiTimeout,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        ),
      );

      // Add interceptor for logging
      _dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            _logger.d('🔵 ${options.method} ${options.baseUrl}${options.path}');
            handler.next(options);
          },
          onResponse: (response, handler) {
            _logger.d(
              '🟢 ${response.statusCode} ${response.requestOptions.path}',
            );
            handler.next(response);
          },
          onError: (error, handler) {
            _logger.e(
              '🔴 ${error.response?.statusCode} ${error.requestOptions.path}: ${error.message}',
            );
            handler.next(error);
          },
        ),
      );
    } catch (e) {
      rethrow;
    }
  }

  /// Handle Dio errors and convert to ApiException
  ApiException _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return const ApiException(message: 'Connection timeout');
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final message =
            error.response?.data?['message'] ?? 'Server error occurred';
        return ApiException(message: message, statusCode: statusCode);
      case DioExceptionType.cancel:
        return const ApiException(message: 'Request cancelled');
      default:
        return const ApiException(message: 'Network error occurred');
    }
  }

  /// GET - Fetch list
  Future<List<T>> getList<T>(
    String endpoint,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.get(endpoint);
      final List<dynamic> data = response.data['data'] ?? response.data;
      return data.map((item) => fromJson(item)).toList();
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// GET - Fetch by ID
  Future<T> getById<T>(
    String endpoint,
    String id,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final path = id.isEmpty ? endpoint : '$endpoint/$id';
      final response = await _dio.get(path);
      final Map<String, dynamic> data = response.data['data'] ?? response.data;
      return fromJson(data);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// GET - Single resource (no ID needed)
  Future<T> get<T>(
    String endpoint,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.get(endpoint);
      final Map<String, dynamic> data = response.data['data'] ?? response.data;
      return fromJson(data);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// POST - Create
  Future<T> create<T>(
    String endpoint,
    Map<String, dynamic> data,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.post(endpoint, data: data);
      final Map<String, dynamic> responseData =
          response.data['data'] ?? response.data;
      return fromJson(responseData);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// POST - Form URL Encoded (for OAuth2)
  Future<T> postForm<T>(
    String endpoint,
    Map<String, dynamic> data,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.post(
        endpoint,
        data: data,
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );
      final Map<String, dynamic> responseData =
          response.data['data'] ?? response.data;
      return fromJson(responseData);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// PUT - Update
  Future<T> update<T>(
    String endpoint,
    String id,
    Map<String, dynamic> data,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.put('$endpoint/$id', data: data);
      final Map<String, dynamic> responseData =
          response.data['data'] ?? response.data;
      return fromJson(responseData);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// PUT - Update without ID (for endpoints that don't require ID in path)
  Future<T> updateProfile<T>(
    String endpoint,
    Map<String, dynamic> data,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final response = await _dio.put(endpoint, data: data);
      final Map<String, dynamic> responseData =
          response.data['data'] ?? response.data;
      return fromJson(responseData);
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// DELETE
  Future<void> delete(String endpoint, String id) async {
    try {
      await _dio.delete('$endpoint/$id');
    } on DioException catch (error) {
      throw _handleError(error);
    }
  }

  /// Set Authorization Token
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// Clear Authorization Token
  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
  }
}

/// Provider for SimpleApiService
final apiProvider = Provider<ApiService>((ref) => ApiService());
