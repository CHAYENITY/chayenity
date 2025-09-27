import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 🌐 Global HTTP Service - ใช้ร่วมกันทุก feature
class HttpService {
  static HttpService? _instance;
  late final Dio _dio;

  // Singleton pattern
  static HttpService get instance => _instance ??= HttpService._();

  HttpService._() {
    _dio = Dio(
      BaseOptions(
        baseUrl: 'http://localhost:8000', // 🔧 เปลี่ยน URL ตาม server
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _setupInterceptors();
  }

  void _setupInterceptors() {
    // 📝 Logging (เฉพาะ debug mode)
    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          logPrint: (log) => debugPrint('🌐 HTTP: $log'),
        ),
      );
    }

    // 🔐 Auth Token Interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // TODO: เพิ่ม token จาก storage
          // final token = TokenStorage.getToken();
          // if (token != null) {
          //   options.headers['Authorization'] = 'Bearer $token';
          // }
          handler.next(options);
        },
        onError: (error, handler) {
          if (error.response?.statusCode == 401) {
            // TODO: Handle token expired
            debugPrint('🔐 Token expired');
          }
          handler.next(error);
        },
      ),
    );
  }

  // 🚀 Simple HTTP Methods
  Future<T> get<T>(String path, {Map<String, dynamic>? params}) async {
    try {
      final response = await _dio.get(path, queryParameters: params);
      return response.data as T;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<T> post<T>(String path, {dynamic data}) async {
    try {
      final response = await _dio.post(path, data: data);
      return response.data as T;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<T> put<T>(String path, {dynamic data}) async {
    try {
      final response = await _dio.put(path, data: data);
      return response.data as T;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<T> delete<T>(String path) async {
    try {
      final response = await _dio.delete(path);
      return response.data as T;
    } catch (e) {
      throw _handleError(e);
    }
  }

  // 🛠️ Error Handler
  Exception _handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
          return const HttpException('Connection timeout');
        case DioExceptionType.receiveTimeout:
          return const HttpException('Receive timeout');
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          final message =
              error.response?.data?['detail'] ??
              error.response?.data?['message'] ??
              'Server error';
          return HttpException('$message (${statusCode ?? 'Unknown'})');
        default:
          return HttpException(error.message ?? 'Network error');
      }
    }
    return HttpException(error.toString());
  }
}

/// 🔥 Custom Exception
class HttpException implements Exception {
  final String message;
  const HttpException(this.message);

  @override
  String toString() => message;
}

/// 🎯 Riverpod Provider
final httpServiceProvider = Provider<HttpService>(
  (ref) => HttpService.instance,
);
