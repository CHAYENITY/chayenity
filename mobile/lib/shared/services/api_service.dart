import 'package:dio/dio.dart';
import 'package:chayenity/shared/constants/api_endpoints.dart';
import 'package:chayenity/shared/models/api.dart';
import 'package:logger/logger.dart';

/// Generic API service for CRUD operations
class ApiService {
  late final Dio _dio;
  late final Logger _logger;

  ApiService() {
    _logger = Logger();
    _dio = Dio(BaseOptions(
      baseUrl: ApiEndpoints.apiUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptors
    _dio.interceptors.add(_createLoggingInterceptor());
    _dio.interceptors.add(_createErrorInterceptor());
  }

  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  /// GET request - สำหรับดึงข้อมูลรายการ (with pagination)
  Future<ApiPaginatedResponse<T>> getList<T>(
    String endpoint, {
    PaginationParams? pagination,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔍 GET List: $endpoint');
      
      final response = await _dio.get(
        endpoint,
        queryParameters: pagination?.toJson(),
      );

      // Check if response is successful
      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiPaginatedResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiPaginatedResponse<T>.fromJson(
        responseData,
        (json) => json as T,
      );
    } catch (e) {
      _logger.e('❌ Error getting list from $endpoint: $e');
      rethrow;
    }
  }

  /// GET request - สำหรับดึงข้อมูลรายการเดียว
  Future<ApiResponse<T>> getById<T>(
    String endpoint,
    dynamic id, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔍 GET By ID: $endpoint/$id');
      
      final response = await _dio.get(
        '$endpoint/$id',
        queryParameters: queryParameters,
      );

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error getting item by ID from $endpoint: $e');
      rethrow;
    }
  }

  /// POST request - สำหรับสร้างข้อมูลใหม่
  Future<ApiResponse<T>> create<T>(
    String endpoint,
    Map<String, dynamic> data, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('✅ POST Create: $endpoint');
      
      final response = await _dio.post(endpoint, data: data);

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error creating item at $endpoint: $e');
      rethrow;
    }
  }

  /// PUT request - สำหรับอัปเดตข้อมูลทั้งหมด
  Future<ApiResponse<T>> update<T>(
    String endpoint,
    dynamic id,
    Map<String, dynamic> data, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔄 PUT Update: $endpoint/$id');
      
      final response = await _dio.put('$endpoint/$id', data: data);

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error updating item at $endpoint: $e');
      rethrow;
    }
  }

  /// PATCH request - สำหรับอัปเดตข้อมูลบางส่วน
  Future<ApiResponse<T>> patch<T>(
    String endpoint,
    dynamic id,
    Map<String, dynamic> data, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔄 PATCH Update: $endpoint/$id');
      
      final response = await _dio.patch('$endpoint/$id', data: data);

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error patching item at $endpoint: $e');
      rethrow;
    }
  }

  /// DELETE request - สำหรับลบข้อมูล
  Future<ApiResponse<bool>> delete(String endpoint, dynamic id) async {
    try {
      _logger.i('🗑️ DELETE: $endpoint/$id');
      
      final response = await _dio.delete('$endpoint/$id');
      
      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }
      
      return ApiResponse<bool>(
        data: responseData['success'],
        message: responseData['message'],
        success: responseData['success'],
      );
    } catch (e) {
      _logger.e('❌ Error deleting item from $endpoint: $e');
      rethrow;
    }
  }

  /// Custom GET request - สำหรับ endpoint พิเศษ
  Future<ApiResponse<T>> customGet<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔧 Custom GET: $endpoint');
      
      final response = await _dio.get(
        endpoint,
        queryParameters: queryParameters,
      );

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error in custom GET $endpoint: $e');
      rethrow;
    }
  }

  /// Custom POST request - สำหรับ endpoint พิเศษ
  Future<ApiResponse<T>> customPost<T>(
    String endpoint,
    Map<String, dynamic> data, {
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      _logger.i('🔧 Custom POST: $endpoint');
      
      final response = await _dio.post(endpoint, data: data);

      final responseData = response.data as Map<String, dynamic>;
      
      if (!responseData['success']) {
        throw Exception(responseData['message'] ?? 'API request failed');
      }

      if (fromJson != null) {
        return ApiResponse<T>.fromJson(responseData, fromJson);
      }
      
      // If no fromJson provided, assume T is Map<String, dynamic>
      return ApiResponse<T>.fromJson(responseData, (json) => json as T);
    } catch (e) {
      _logger.e('❌ Error in custom POST $endpoint: $e');
      rethrow;
    }
  }

  /// Set authorization token
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
    _logger.i('🔑 Auth token set');
  }

  /// Remove authorization token
  void removeAuthToken() {
    _dio.options.headers.remove('Authorization');
    _logger.i('🔑 Auth token removed');
  }

  /// Create logging interceptor
  Interceptor _createLoggingInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        _logger.d(
          '🚀 Request: ${options.method} ${options.path}\n'
          'Headers: ${options.headers}\n'
          'Data: ${options.data}',
        );
        handler.next(options);
      },
      onResponse: (response, handler) {
        _logger.d(
          '✅ Response: ${response.statusCode} ${response.requestOptions.path}\n'
          'Data: ${response.data}',
        );
        handler.next(response);
      },
      onError: (error, handler) {
        _logger.e(
          '❌ Error: ${error.response?.statusCode} ${error.requestOptions.path}\n'
          'Message: ${error.message}\n'
          'Data: ${error.response?.data}',
        );
        handler.next(error);
      },
    );
  }

  /// Create error interceptor
  Interceptor _createErrorInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) {
        // Handle different types of errors
        if (error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.receiveTimeout) {
          error = error.copyWith(message: 'Connection timeout. Please try again.');
        } else if (error.type == DioExceptionType.connectionError) {
          error = error.copyWith(message: 'No internet connection.');
        } else if (error.response?.statusCode == 401) {
          error = error.copyWith(message: 'Unauthorized. Please login again.');
        } else if (error.response?.statusCode == 403) {
          error = error.copyWith(message: 'Access forbidden.');
        } else if (error.response?.statusCode == 404) {
          error = error.copyWith(message: 'Resource not found.');
        } else if (error.response?.statusCode == 500) {
          error = error.copyWith(message: 'Server error. Please try again later.');
        }
        
        handler.next(error);
      },
    );
  }
}
