import 'http_service.dart';

/// Generic CRUD Service (เหมือนแนวคิด crud.ts ใน React)
abstract class CrudService<T> {
  final HttpService http;
  final String endpoint;

  CrudService(this.http, this.endpoint);

  T fromJson(Map<String, dynamic> json);
  Map<String, dynamic> toJson(T data);

  Future<List<T>> getAll({Map<String, dynamic>? params}) async {
    final result = await http.get<Map<String, dynamic>>(
      endpoint,
      params: params,
    );
    final items = (result['items'] ?? result['data'] ?? result as List)
        .map<T>((json) => fromJson(json as Map<String, dynamic>))
        .toList();
    return items;
  }

  Future<T> getById(String id) async {
    final result = await http.get<Map<String, dynamic>>('$endpoint/$id');
    return fromJson(result);
  }

  Future<T> create(T data) async {
    final result = await http.post<Map<String, dynamic>>(
      endpoint,
      data: toJson(data),
    );
    return fromJson(result);
  }

  Future<T> update(String id, T data) async {
    final result = await http.put<Map<String, dynamic>>(
      '$endpoint/$id',
      data: toJson(data),
    );
    return fromJson(result);
  }

  Future<void> delete(String id) async {
    await http.delete('$endpoint/$id');
  }
}
