import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile_setup_model.freezed.dart';
part 'profile_setup_model.g.dart';

@freezed
class AddressModel with _$AddressModel {
  const factory AddressModel({
    @Default('') String addressText,
    @Default('') String district,
    @Default('') String province,
    @Default('') String postalCode,
    @Default('Thailand') String country,
    @Default(0.0) double latitude,
    @Default(0.0) double longitude,
  }) = _AddressModel;

  const AddressModel._();

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    return AddressModel(
      addressText: json['address_text'] as String? ?? '',
      district: json['district'] as String? ?? '',
      province: json['province'] as String? ?? '',
      postalCode: json['postal_code'] as String? ?? '',
      country: json['country'] as String? ?? 'Thailand',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'address_text': addressText,
    'district': district,
    'province': province,
    'postal_code': postalCode,
    'country': country,
    'latitude': latitude,
    'longitude': longitude,
  };
}

@freezed
class ProfileSetupModel with _$ProfileSetupModel {
  const factory ProfileSetupModel({
    @Default('') String firstName,
    @Default('') String lastName,
    @Default('') String bio,
    @Default('') String phoneNumber,
    @Default('') String additionalContact,
    String? profileImageUrl,
    AddressModel? address,
    // Local-only fields for UI (not sent to API)
    String? profileImagePath,
    String? citizenIdImagePath,
    @Default(false) bool isVerified,
    // Step tracking (local only)
    @Default(1) int currentStep,
    @Default(false) bool isStep1Complete,
    @Default(false) bool isStep2Complete,
    @Default(false) bool isStep3Complete,
  }) = _ProfileSetupModel;

  const ProfileSetupModel._();

  factory ProfileSetupModel.fromJson(Map<String, dynamic> json) {
    return ProfileSetupModel(
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      bio: json['bio'] as String? ?? '',
      phoneNumber: json['phone_number'] as String? ?? '',
      additionalContact: json['additional_contact'] as String? ?? '',
      profileImageUrl: json['profile_image_url'] as String?,
      address: json['address'] != null
          ? AddressModel.fromJson(json['address'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toApiJson() => {
    'first_name': firstName,
    'last_name': lastName,
    'bio': bio,
    'phone_number': phoneNumber,
    'additional_contact': additionalContact,
    if (profileImageUrl != null) 'profile_image_url': profileImageUrl,
    if (address != null) 'address': address!.toJson(),
  };

  bool get canProceedToStep2 =>
      firstName.isNotEmpty && lastName.isNotEmpty && phoneNumber.isNotEmpty;

  bool get canProceedToStep3 =>
      canProceedToStep2 &&
      address != null &&
      address!.district.isNotEmpty &&
      address!.province.isNotEmpty;

  bool get canComplete => canProceedToStep3 && citizenIdImagePath != null;
}
