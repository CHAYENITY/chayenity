import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    String? firstName,
    String? lastName,
    String? bio,
    String? phoneNumber,
    String? additionalContact,
    @Default(false) bool isProfileSetup,
    String? profileImageUrl,
    @Default(false) bool isVerified,
    @Default(5.0) double reputationScore,
    DateTime? createdAt,
    List<dynamic>? addresses,
  }) = _User;

  const User._();

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      bio: json['bio'] as String?,
      phoneNumber: json['phone_number'] as String?,
      additionalContact: json['additional_contact'] as String?,
      isProfileSetup: json['is_profile_setup'] as bool? ?? false,
      profileImageUrl: json['profile_image_url'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      reputationScore: (json['reputation_score'] as num?)?.toDouble() ?? 5.0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      addresses: json['addresses'] as List<dynamic>?,
    );
  }

  String get displayName {
    if (firstName != null || lastName != null) {
      return '${firstName ?? ''} ${lastName ?? ''}'.trim();
    }
    return email.split('@').first;
  }

  Map<String, dynamic> toCreateJson() => {'email': email};
}
