import 'package:freezed_annotation/freezed_annotation.dart';

part 'api.freezed.dart';
part 'api.g.dart';

/// API Response Types for GetById, Create, Update, Delete
@Freezed(genericArgumentFactories: true)
class ApiResponse<T> with _$ApiResponse<T> {
  const factory ApiResponse({
    /// ข้อมูลที่คืนจาก API
    /// - GET (เช่น getById): มักจะมี data เสมอ
    /// - CREATE, UPDATE, DELETE: โดยทั่วไปจะไม่มี data (อาจเป็น null)
    ///   ยกเว้นกรณีที่ API ต้องการคืนข้อมูลใหม่ เช่น id ที่ถูกสร้าง หรือข้อมูลที่ backend ปรับแต่ง
    /// - การคืน data ขึ้นอยู่กับความจำเป็นของแต่ละ API endpoint
    required T data,
    required String message, // 'Success' หรือ 'Error'
    required bool success, // true หรือ false
  }) = _ApiResponse<T>;

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object?) fromJsonT,
  ) => _$ApiResponseFromJson(json, fromJsonT);
}

/// API Response for GetAll with Pagination
@Freezed(genericArgumentFactories: true)
class ApiPaginatedResponse<T> with _$ApiPaginatedResponse<T> {
  const factory ApiPaginatedResponse({
    required List<T> data,
    required PaginationMeta meta,
    required String message, // 'Success' หรือ 'Error'
    required bool success, // true หรือ false
  }) = _ApiPaginatedResponse<T>;

  factory ApiPaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object?) fromJsonT,
  ) => _$ApiPaginatedResponseFromJson(json, fromJsonT);
}

/// Pagination Metadata
@freezed
class PaginationMeta with _$PaginationMeta {
  const factory PaginationMeta({
    required int total,
    required int page,
    required int limit,
    required int totalPages,
  }) = _PaginationMeta;

  factory PaginationMeta.fromJson(Map<String, dynamic> json) =>
      _$PaginationMetaFromJson(json);
}

/// API Request Types for Pagination
@freezed
class PaginationParams with _$PaginationParams {
  const factory PaginationParams({
    @Default(1) int page,
    @Default(10) int limit,
    String? search,
    String? sortBy,
    @Default('asc') String sortOrder, // 'asc' หรือ 'desc'
  }) = _PaginationParams;

  factory PaginationParams.fromJson(Map<String, dynamic> json) =>
      _$PaginationParamsFromJson(json);
}

/// API Exception
@freezed
class ApiException with _$ApiException {
  const factory ApiException({
    required String message,
    int? statusCode,
    dynamic data,
  }) = _ApiException;

  factory ApiException.fromJson(Map<String, dynamic> json) =>
      _$ApiExceptionFromJson(json);
}
