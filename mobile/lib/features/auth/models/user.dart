import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

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

@freezed
class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    required String email,
    required String password,
  }) = _LoginRequest;

  const LoginRequest._();
  factory LoginRequest.fromJson(Map<String, dynamic> json) =>
      _$LoginRequestFromJson(json);

  // OAuth2 Password Flow format
  Map<String, dynamic> toFormData() => {
    'grant_type': 'password',
    'username': email,
    'password': password,
    'scope': '',
    'client_id': '',
    'client_secret': '',
  };
}

@freezed
class LoginResponse with _$LoginResponse {
  const factory LoginResponse({
    required String accessToken,
    required String refreshToken,
    @Default(false) bool isProfileSetup,
    @Default('bearer') String tokenType,
  }) = _LoginResponse;

  const LoginResponse._();
  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);
}

@freezed
class RefreshTokenResponse with _$RefreshTokenResponse {
  const factory RefreshTokenResponse({
    required String accessToken,
    @Default('bearer') String tokenType,
  }) = _RefreshTokenResponse;

  const RefreshTokenResponse._();
  factory RefreshTokenResponse.fromJson(Map<String, dynamic> json) =>
      _$RefreshTokenResponseFromJson(json);
}

@freezed
class RegisterRequest with _$RegisterRequest {
  const factory RegisterRequest({
    required String email,
    required String password,
    required String confirmPassword,
  }) = _RegisterRequest;

  const RegisterRequest._();
  factory RegisterRequest.fromJson(Map<String, dynamic> json) =>
      _$RegisterRequestFromJson(json);

  @override
  Map<String, dynamic> toJson() => {'email': email, 'password': password};

  bool get isPasswordMatch => password == confirmPassword;
}
