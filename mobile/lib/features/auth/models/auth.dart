import 'package:freezed_annotation/freezed_annotation.dart';

part 'auth.freezed.dart';
part 'auth.g.dart';

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
