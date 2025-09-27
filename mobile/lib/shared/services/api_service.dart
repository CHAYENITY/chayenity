import 'http_service.dart';
import 'constants/api_endpoints.dart';

/// API Service (เหมือน api.ts ใน React)
class ApiService {
  final HttpService http;
  ApiService(this.http);

  Future<T> get<T>(String path, {Map<String, dynamic>? params}) async {
    return await http.get<T>(path, params: params);
  }

  Future<T> post<T>(String path, {dynamic data}) async {
    return await http.post<T>(path, data: data);
  }

  Future<T> put<T>(String path, {dynamic data}) async {
    return await http.put<T>(path, data: data);
  }

  Future<T> delete<T>(String path) async {
    return await http.delete<T>(path);
  }
}
