import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import '../models/profile_setup_model.dart';
import '../services/profile_setup_service.dart';

final profileSetupServiceProvider = Provider<ProfileSetupService>((ref) {
  return ProfileSetupService(ref.read(apiProvider));
});

final profileSetupProvider =
    StateNotifierProvider<ProfileSetupNotifier, ProfileSetupModel>((ref) {
      return ProfileSetupNotifier(ref);
    });

class ProfileSetupNotifier extends StateNotifier<ProfileSetupModel> {
  ProfileSetupNotifier(this._ref) : super(const ProfileSetupModel());
  final Ref _ref;

  // Step 1: Basic Information
  void updateBasicInfo({
    String? firstName,
    String? lastName,
    String? bio,
    String? phoneNumber,
    String? additionalContact,
  }) {
    state = state.copyWith(
      firstName: firstName ?? state.firstName,
      lastName: lastName ?? state.lastName,
      bio: bio ?? state.bio,
      phoneNumber: phoneNumber ?? state.phoneNumber,
      additionalContact: additionalContact ?? state.additionalContact,
    );
  }

  void updateProfileImage(String? imagePath) {
    state = state.copyWith(profileImagePath: imagePath);
  }

  void completeStep1() {
    if (state.canProceedToStep2) {
      state = state.copyWith(isStep1Complete: true, currentStep: 2);
    }
  }

  // Step 2: Location
  void updateAddress({
    String? addressText,
    String? district,
    String? province,
    String? postalCode,
    String? country,
    double? latitude,
    double? longitude,
  }) {
    final currentAddress = state.address ?? const AddressModel();
    final updatedAddress = currentAddress.copyWith(
      addressText: addressText ?? currentAddress.addressText,
      district: district ?? currentAddress.district,
      province: province ?? currentAddress.province,
      postalCode: postalCode ?? currentAddress.postalCode,
      country: country ?? currentAddress.country,
      latitude: latitude ?? currentAddress.latitude,
      longitude: longitude ?? currentAddress.longitude,
    );
    state = state.copyWith(address: updatedAddress);
  }

  void confirmCurrentLocation(double latitude, double longitude) {
    final currentAddress = state.address ?? const AddressModel();
    state = state.copyWith(
      address: currentAddress.copyWith(
        latitude: latitude,
        longitude: longitude,
      ),
    );
  }

  void completeStep2() {
    if (state.canProceedToStep3) {
      state = state.copyWith(isStep2Complete: true, currentStep: 3);
    }
  }

  // Step 3: Citizen ID Verification
  void updateCitizenIdImage(String? imagePath) {
    state = state.copyWith(citizenIdImagePath: imagePath);
  }

  void completeStep3() {
    if (state.canComplete) {
      state = state.copyWith(isStep3Complete: true, isVerified: true);
    }
  }

  // Navigation
  void goToStep(int step) {
    if (step >= 1 && step <= 3) {
      state = state.copyWith(currentStep: step);
    }
  }

  void nextStep() {
    if (state.currentStep < 3) {
      state = state.copyWith(currentStep: state.currentStep + 1);
    }
  }

  void previousStep() {
    if (state.currentStep > 1) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }

  // Submit Profile
  Future<bool> submitProfile() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('submit-profile');

      final service = _ref.read(profileSetupServiceProvider);

      // Upload images if present
      if (state.profileImagePath != null) {
        await service.uploadProfileImage(state.profileImagePath!);
      }

      if (state.citizenIdImagePath != null) {
        await service.uploadCitizenIdImage(state.citizenIdImagePath!);
      }

      // Submit profile data
      await service.submitProfile(state);

      return true;
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError(
            'Failed to submit profile: $e',
            context: 'submitProfile',
          );
      return false;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('submit-profile');
    }
  }

  // Reset state
  void reset() {
    state = const ProfileSetupModel();
  }
}

// Helper providers for provinces and districts
final provincesProvider = FutureProvider<List<Map<String, String>>>((
  ref,
) async {
  final service = ref.read(profileSetupServiceProvider);
  return await service.getProvinces();
});

final districtsProvider =
    FutureProvider.family<List<Map<String, String>>, String>((
      ref,
      provinceId,
    ) async {
      final service = ref.read(profileSetupServiceProvider);
      return await service.getDistricts(provinceId);
    });
