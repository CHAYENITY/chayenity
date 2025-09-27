import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:chayenity/shared/services/api_service.dart';
import 'package:chayenity/shared/models/api.dart';

/// Provider สำหรับ ApiService
final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

/// Base class สำหรับ Query state
@immutable
class QueryState<T> {
  final T? data;
  final bool isLoading;
  final String? error;
  final bool hasError;

  const QueryState({
    this.data,
    this.isLoading = false,
    this.error,
    this.hasError = false,
  });

  QueryState<T> copyWith({
    T? data,
    bool? isLoading,
    String? error,
    bool? hasError,
  }) {
    return QueryState<T>(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      hasError: hasError ?? this.hasError,
    );
  }
}

/// Base class สำหรับ Paginated Query state
@immutable
class PaginatedQueryState<T> {
  final List<T>? data;
  final PaginationMeta? meta;
  final bool isLoading;
  final String? error;
  final bool hasError;

  const PaginatedQueryState({
    this.data,
    this.meta,
    this.isLoading = false,
    this.error,
    this.hasError = false,
  });

  PaginatedQueryState<T> copyWith({
    List<T>? data,
    PaginationMeta? meta,
    bool? isLoading,
    String? error,
    bool? hasError,
  }) {
    return PaginatedQueryState<T>(
      data: data ?? this.data,
      meta: meta ?? this.meta,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      hasError: hasError ?? this.hasError,
    );
  }
}

/// Base class สำหรับ Mutation state
@immutable
class MutationState<T> {
  final T? data;
  final bool isLoading;
  final String? error;
  final bool hasError;
  final bool isSuccess;

  const MutationState({
    this.data,
    this.isLoading = false,
    this.error,
    this.hasError = false,
    this.isSuccess = false,
  });

  MutationState<T> copyWith({
    T? data,
    bool? isLoading,
    String? error,
    bool? hasError,
    bool? isSuccess,
  }) {
    return MutationState<T>(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      hasError: hasError ?? this.hasError,
      isSuccess: isSuccess ?? this.isSuccess,
    );
  }
}

/// Generic Entity List Query Provider (with pagination)
class EntityListNotifier<T> extends StateNotifier<PaginatedQueryState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final T Function(Map<String, dynamic>)? fromJson;
  PaginationParams? _currentPagination;

  EntityListNotifier(
    this._apiService, {
    required this.endpoint,
    this.fromJson,
    PaginationParams? pagination,
  }) : super(const PaginatedQueryState(isLoading: true)) {
    _currentPagination = pagination;
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      state = state.copyWith(isLoading: true, hasError: false, error: null);
      
      final response = await _apiService.getList<T>(
        endpoint,
        pagination: _currentPagination,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        meta: response.meta,
        isLoading: false,
        hasError: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh([PaginationParams? pagination]) async {
    if (pagination != null) {
      _currentPagination = pagination;
    }
    await _fetchData();
  }

  Future<void> loadPage(int page) async {
    _currentPagination = (_currentPagination ?? const PaginationParams()).copyWith(page: page);
    await _fetchData();
  }

  Future<void> search(String query) async {
    _currentPagination = (_currentPagination ?? const PaginationParams()).copyWith(search: query, page: 1);
    await _fetchData();
  }

  Future<void> sort(String sortBy, String sortOrder) async {
    _currentPagination = (_currentPagination ?? const PaginationParams()).copyWith(
      sortBy: sortBy,
      sortOrder: sortOrder,
      page: 1,
    );
    await _fetchData();
  }
}

/// Generic Entity By ID Query Provider
class EntityByIdNotifier<T> extends StateNotifier<QueryState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final dynamic id;
  final T Function(Map<String, dynamic>)? fromJson;
  final Map<String, dynamic>? queryParameters;

  EntityByIdNotifier(
    this._apiService, {
    required this.endpoint,
    required this.id,
    this.fromJson,
    this.queryParameters,
  }) : super(const QueryState(isLoading: true)) {
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      state = state.copyWith(isLoading: true, hasError: false, error: null);
      
      final response = await _apiService.getById<T>(
        endpoint,
        id,
        queryParameters: queryParameters,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() async {
    await _fetchData();
  }
}

/// Generic Create Mutation Provider
class CreateMutationNotifier<T> extends StateNotifier<MutationState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final T Function(Map<String, dynamic>)? fromJson;

  CreateMutationNotifier(
    this._apiService, {
    required this.endpoint,
    this.fromJson,
  }) : super(const MutationState());

  Future<void> mutate(Map<String, dynamic> data) async {
    try {
      state = state.copyWith(
        isLoading: true,
        hasError: false,
        error: null,
        isSuccess: false,
      );
      
      final response = await _apiService.create<T>(
        endpoint,
        data,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
        isSuccess: response.success,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
        isSuccess: false,
      );
    }
  }

  void reset() {
    state = const MutationState();
  }
}

/// Generic Update Mutation Provider
class UpdateMutationNotifier<T> extends StateNotifier<MutationState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final T Function(Map<String, dynamic>)? fromJson;

  UpdateMutationNotifier(
    this._apiService, {
    required this.endpoint,
    this.fromJson,
  }) : super(const MutationState());

  Future<void> mutate(dynamic id, Map<String, dynamic> data) async {
    try {
      state = state.copyWith(
        isLoading: true,
        hasError: false,
        error: null,
        isSuccess: false,
      );
      
      final response = await _apiService.update<T>(
        endpoint,
        id,
        data,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
        isSuccess: response.success,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
        isSuccess: false,
      );
    }
  }

  Future<void> patch(dynamic id, Map<String, dynamic> data) async {
    try {
      state = state.copyWith(
        isLoading: true,
        hasError: false,
        error: null,
        isSuccess: false,
      );
      
      final response = await _apiService.patch<T>(
        endpoint,
        id,
        data,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
        isSuccess: response.success,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
        isSuccess: false,
      );
    }
  }

  void reset() {
    state = const MutationState();
  }
}

/// Generic Delete Mutation Provider
class DeleteMutationNotifier extends StateNotifier<MutationState<bool>> {
  final ApiService _apiService;
  final String endpoint;

  DeleteMutationNotifier(
    this._apiService, {
    required this.endpoint,
  }) : super(const MutationState());

  Future<void> mutate(dynamic id) async {
    try {
      state = state.copyWith(
        isLoading: true,
        hasError: false,
        error: null,
        isSuccess: false,
      );
      
      final response = await _apiService.delete(endpoint, id);
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
        isSuccess: response.success,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
        isSuccess: false,
      );
    }
  }

  void reset() {
    state = const MutationState();
  }
}

/// Custom Query Provider สำหรับ endpoint พิเศษ
class CustomQueryNotifier<T> extends StateNotifier<QueryState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final T Function(Map<String, dynamic>)? fromJson;
  final Map<String, dynamic>? queryParameters;

  CustomQueryNotifier(
    this._apiService, {
    required this.endpoint,
    this.fromJson,
    this.queryParameters,
  }) : super(const QueryState(isLoading: true)) {
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      state = state.copyWith(isLoading: true, hasError: false, error: null);
      
      final response = await _apiService.customGet<T>(
        endpoint,
        queryParameters: queryParameters,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() async {
    await _fetchData();
  }
}

/// Custom Mutation Provider สำหรับ endpoint พิเศษ
class CustomMutationNotifier<T> extends StateNotifier<MutationState<T>> {
  final ApiService _apiService;
  final String endpoint;
  final T Function(Map<String, dynamic>)? fromJson;

  CustomMutationNotifier(
    this._apiService, {
    required this.endpoint,
    this.fromJson,
  }) : super(const MutationState());

  Future<void> mutate(Map<String, dynamic> data) async {
    try {
      state = state.copyWith(
        isLoading: true,
        hasError: false,
        error: null,
        isSuccess: false,
      );
      
      final response = await _apiService.customPost<T>(
        endpoint,
        data,
        fromJson: fromJson,
      );
      
      state = state.copyWith(
        data: response.data,
        isLoading: false,
        hasError: false,
        error: null,
        isSuccess: response.success,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasError: true,
        error: e.toString(),
        isSuccess: false,
      );
    }
  }

  void reset() {
    state = const MutationState();
  }
}

/// ========== HELPER FUNCTIONS FOR EASY USAGE ==========

/// สร้าง Provider สำหรับ Entity List (with pagination)
StateNotifierProvider<EntityListNotifier<T>, PaginatedQueryState<T>> 
useEntityList<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  PaginationParams? pagination,
  String? name,
}) {
  return StateNotifierProvider<EntityListNotifier<T>, PaginatedQueryState<T>>(
    (ref) => EntityListNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      fromJson: fromJson,
      pagination: pagination,
    ),
    name: name ?? 'EntityListProvider_$endpoint',
  );
}

/// สร้าง Provider สำหรับ Entity By ID
StateNotifierProvider<EntityByIdNotifier<T>, QueryState<T>>
useEntityById<T>(
  String endpoint,
  dynamic id, {
  T Function(Map<String, dynamic>)? fromJson,
  Map<String, dynamic>? queryParameters,
  String? name,
}) {
  return StateNotifierProvider<EntityByIdNotifier<T>, QueryState<T>>(
    (ref) => EntityByIdNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      id: id,
      fromJson: fromJson,
      queryParameters: queryParameters,
    ),
    name: name ?? 'EntityByIdProvider_${endpoint}_$id',
  );
}

/// สร้าง Provider สำหรับ Create Mutation
StateNotifierProvider<CreateMutationNotifier<T>, MutationState<T>>
useCreateEntity<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
}) {
  return StateNotifierProvider<CreateMutationNotifier<T>, MutationState<T>>(
    (ref) => CreateMutationNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      fromJson: fromJson,
    ),
    name: name ?? 'CreateMutationProvider_$endpoint',
  );
}

/// สร้าง Provider สำหรับ Update Mutation
StateNotifierProvider<UpdateMutationNotifier<T>, MutationState<T>>
useUpdateEntity<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
}) {
  return StateNotifierProvider<UpdateMutationNotifier<T>, MutationState<T>>(
    (ref) => UpdateMutationNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      fromJson: fromJson,
    ),
    name: name ?? 'UpdateMutationProvider_$endpoint',
  );
}

/// สร้าง Provider สำหรับ Delete Mutation
StateNotifierProvider<DeleteMutationNotifier, MutationState<bool>>
useDeleteEntity(
  String endpoint, {
  String? name,
}) {
  return StateNotifierProvider<DeleteMutationNotifier, MutationState<bool>>(
    (ref) => DeleteMutationNotifier(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
    ),
    name: name ?? 'DeleteMutationProvider_$endpoint',
  );
}

/// สร้าง Provider สำหรับ Custom Query
StateNotifierProvider<CustomQueryNotifier<T>, QueryState<T>>
useCustomQuery<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  Map<String, dynamic>? queryParameters,
  String? name,
}) {
  return StateNotifierProvider<CustomQueryNotifier<T>, QueryState<T>>(
    (ref) => CustomQueryNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      fromJson: fromJson,
      queryParameters: queryParameters,
    ),
    name: name ?? 'CustomQueryProvider_$endpoint',
  );
}

/// สร้าง Provider สำหรับ Custom Mutation
StateNotifierProvider<CustomMutationNotifier<T>, MutationState<T>>
useCustomMutation<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
}) {
  return StateNotifierProvider<CustomMutationNotifier<T>, MutationState<T>>(
    (ref) => CustomMutationNotifier<T>(
      ref.read(apiServiceProvider),
      endpoint: endpoint,
      fromJson: fromJson,
    ),
    name: name ?? 'CustomMutationProvider_$endpoint',
  );
}