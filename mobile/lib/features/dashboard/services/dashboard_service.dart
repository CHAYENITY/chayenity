import 'package:hourz/shared/providers/index.dart';
import '../models/index.dart';

class DashboardService {
  final ApiService _apiService;
  static const String _gigsEndpoint = '/gigs';
  static const String _categoriesEndpoint = '/categories';

  DashboardService(this._apiService);

  /// ดึงรายการ gigs ทั้งหมด
  Future<List<Gig>> getGigs({String? category, String? search}) async {
    // Note: Query parameters should be handled in API if needed
    // For now, we'll fetch all and filter client-side
    return await _apiService.getList(_gigsEndpoint, Gig.fromJson);
  }

  /// ดึงรายการ categories
  Future<List<Category>> getCategories() async {
    return await _apiService.getList(_categoriesEndpoint, Category.fromJson);
  }

  /// ดึงข้อมูล gig เดียว
  Future<Gig> getGigById(String id) async {
    return await _apiService.getById(_gigsEndpoint, id, Gig.fromJson);
  }
}
