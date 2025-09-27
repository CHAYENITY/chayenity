import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/http_service.dart';

/// Example Riverpod query hook (เหมือน useReactQuery)
final useQueryProvider = FutureProvider.family
    .autoDispose<List<T>, QueryConfig<T>>((ref, config) async {
      final http = ref.watch(httpServiceProvider);
      final result = await http.get<List<dynamic>>(
        config.endpoint,
        params: config.params,
      );
      return result
          .map((json) => config.fromJson(json as Map<String, dynamic>))
          .toList();
    });

class QueryConfig<T> {
  final String endpoint;
  final Map<String, dynamic>? params;
  final T Function(Map<String, dynamic>) fromJson;

  QueryConfig({required this.endpoint, required this.fromJson, this.params});
}
