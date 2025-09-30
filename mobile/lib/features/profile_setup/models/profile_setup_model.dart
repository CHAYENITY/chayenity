import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile_setup_model.freezed.dart';
part 'profile_setup_model.g.dart';

@freezed
class ProfileSetupModel with _$ProfileSetupModel {
  const factory ProfileSetupModel({
    @Default('') String firstName,
    @Default('') String lastName,
    @Default('') String introduction,
    @Default('') String phoneNumber,
    @Default('') String socialContact,
    String? profileImagePath,

    // Location data
    @Default('') String district,
    @Default('') String province,
    @Default('') String address,
    double? latitude,
    double? longitude,

    // Citizen ID data
    String? citizenIdImagePath,
    @Default(false) bool isVerified,

    // Step tracking
    @Default(1) int currentStep,
    @Default(false) bool isStep1Complete,
    @Default(false) bool isStep2Complete,
    @Default(false) bool isStep3Complete,
  }) = _ProfileSetupModel;

  const ProfileSetupModel._();

  factory ProfileSetupModel.fromJson(Map<String, dynamic> json) =>
      _$ProfileSetupModelFromJson(json);

  Map<String, dynamic> toCreateJson() => {
    'first_name': firstName,
    'last_name': lastName,
    'introduction': introduction,
    'phone_number': phoneNumber,
    'social_contact': socialContact,
    'district': district,
    'province': province,
    'address': address,
    'latitude': latitude,
    'longitude': longitude,
    'is_verified': isVerified,
  };

  bool get canProceedToStep2 =>
      firstName.isNotEmpty && lastName.isNotEmpty && phoneNumber.isNotEmpty;

  bool get canProceedToStep3 =>
      canProceedToStep2 &&
      district.isNotEmpty &&
      province.isNotEmpty &&
      latitude != null &&
      longitude != null;

  bool get canComplete => canProceedToStep3 && citizenIdImagePath != null;
}
