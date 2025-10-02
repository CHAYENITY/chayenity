import 'package:hourz/shared/services/api_service.dart';
import '../models/profile_setup_model.dart';

class ProfileSetupService {
  final ApiService _apiService;
  static const String _endpoint = '/auth/profile-setup';

  ProfileSetupService(this._apiService);

  /// Submit profile setup using PUT method
  Future<ProfileSetupModel> submitProfile(ProfileSetupModel profile) async {
    return await _apiService.updateProfile(
      _endpoint,
      profile.toApiJson(),
      ProfileSetupModel.fromJson,
    );
  }

  Future<bool> uploadProfileImage(String imagePath) async {
    try {
      // TODO: Implement image upload to server
      // For now, return true as placeholder
      await Future.delayed(const Duration(seconds: 1));
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> uploadCitizenIdImage(String imagePath) async {
    try {
      // TODO: Implement citizen ID image upload and verification
      // For now, return true as placeholder
      await Future.delayed(const Duration(seconds: 2));
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Map<String, String>>> getProvinces() async {
    try {
      // TODO: Get from real API
      return [
        {'id': '1', 'name': 'กรุงเทพมหานคร'},
        {'id': '2', 'name': 'สงขลา'},
        {'id': '3', 'name': 'เชียงใหม่'},
        {'id': '4', 'name': 'ภูเก็ต'},
      ];
    } catch (e) {
      return [];
    }
  }

  Future<List<Map<String, String>>> getDistricts(String provinceId) async {
    try {
      // TODO: Get from real API
      if (provinceId == '2') {
        // สงขลา
        return [
          {'id': '1', 'name': 'หาดใหญ่'},
          {'id': '2', 'name': 'สงขลา'},
          {'id': '3', 'name': 'สะเดา'},
        ];
      }
      return [
        {'id': '1', 'name': 'เมือง'},
        {'id': '2', 'name': 'อื่นๆ'},
      ];
    } catch (e) {
      return [];
    }
  }
}
