/// API Response Types for Flutter

/// Standard API response for single item operations
/// Used for: GetById, Create, Update, Delete
class ApiResponse<T> {
  /// ข้อมูลที่คืนจาก API
  /// - GET (เช่น getById): มักจะมี data เสมอ
  /// - CREATE, UPDATE, DELETE: โดยทั่วไปจะไม่มี data (อาจเป็น null)
  ///   ยกเว้นกรณีที่ API ต้องการคืนข้อมูลใหม่ เช่น id ที่ถูกสร้าง หรือข้อมูลที่ backend ปรับแต่ง
  /// - การคืน data ขึ้นอยู่กับความจำเป็นของแต่ละ API endpoint
  final T? data;
  
  /// ข้อความตอบกลับจาก API
  /// Success: 'Success'
  /// Error: 'Error message'
  final String message;
  
  /// สถานะความสำเร็จ
  /// true: สำเร็จ
  /// false: ผิดพลาด
  final bool success;

  const ApiResponse({
    required this.data,
    required this.message,
    required this.success,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>)? fromJsonT,
  ) {
    return ApiResponse<T>(
      data: json['data'] != null && fromJsonT != null
          ? fromJsonT(json['data'] as Map<String, dynamic>)
          : json['data'] as T?,
      message: json['message'] as String,
      success: json['success'] as bool,
    );
  }

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T)? toJsonT) {
    return {
      'data': data != null && toJsonT != null ? toJsonT(data as T) : data,
      'message': message,
      'success': success,
    };
  }

  @override
  String toString() {
    return 'ApiResponse{data: $data, message: $message, success: $success}';
  }
}

/// Pagination metadata
class PaginationMeta {
  final int total;
  final int page;
  final int limit;
  final int totalPages;

  const PaginationMeta({
    required this.total,
    required this.page,
    required this.limit,
    required this.totalPages,
  });

  factory PaginationMeta.fromJson(Map<String, dynamic> json) {
    return PaginationMeta(
      total: json['total'] as int,
      page: json['page'] as int,
      limit: json['limit'] as int,
      totalPages: json['totalPages'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total': total,
      'page': page,
      'limit': limit,
      'totalPages': totalPages,
    };
  }

  @override
  String toString() {
    return 'PaginationMeta{total: $total, page: $page, limit: $limit, totalPages: $totalPages}';
  }
}

/// Paginated API response for list operations
/// Used for: GetAll with pagination
class ApiPaginatedResponse<T> {
  final List<T> data;
  final PaginationMeta meta;
  
  /// ข้อความตอบกลับจาก API
  /// Success: 'Success'
  /// Error: 'Error message'
  final String message;
  
  /// สถานะความสำเร็จ
  /// true: สำเร็จ
  /// false: ผิดพลาด
  final bool success;

  const ApiPaginatedResponse({
    required this.data,
    required this.meta,
    required this.message,
    required this.success,
  });

  factory ApiPaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) fromJsonT,
  ) {
    final dataList = json['data'] as List<dynamic>;
    return ApiPaginatedResponse<T>(
      data: dataList
          .map((item) => fromJsonT(item as Map<String, dynamic>))
          .toList(),
      meta: PaginationMeta.fromJson(json['meta'] as Map<String, dynamic>),
      message: json['message'] as String,
      success: json['success'] as bool,
    );
  }

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T) toJsonT) {
    return {
      'data': data.map(toJsonT).toList(),
      'meta': meta.toJson(),
      'message': message,
      'success': success,
    };
  }

  @override
  String toString() {
    return 'ApiPaginatedResponse{data: ${data.length} items, meta: $meta, message: $message, success: $success}';
  }
}

/// Pagination parameters for API requests
class PaginationParams {
  final int? page;
  final int? limit;
  final String? search;
  final String? sortBy;
  final String? sortOrder; // 'asc' | 'desc'

  const PaginationParams({
    this.page,
    this.limit,
    this.search,
    this.sortBy,
    this.sortOrder,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> json = {};
    
    if (page != null) json['page'] = page;
    if (limit != null) json['limit'] = limit;
    if (search != null && search!.isNotEmpty) json['search'] = search;
    if (sortBy != null && sortBy!.isNotEmpty) json['sortBy'] = sortBy;
    if (sortOrder != null && sortOrder!.isNotEmpty) json['sortOrder'] = sortOrder;
    
    return json;
  }

  PaginationParams copyWith({
    int? page,
    int? limit,
    String? search,
    String? sortBy,
    String? sortOrder,
  }) {
    return PaginationParams(
      page: page ?? this.page,
      limit: limit ?? this.limit,
      search: search ?? this.search,
      sortBy: sortBy ?? this.sortBy,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }

  @override
  String toString() {
    return 'PaginationParams{page: $page, limit: $limit, search: $search, sortBy: $sortBy, sortOrder: $sortOrder}';
  }
}