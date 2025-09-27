import 'user_model.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? accessToken;
  final String? refreshToken;
  final String? errorMessage;

  const AuthState({
    required this.status,
    this.user,
    this.accessToken,
    this.refreshToken,
    this.errorMessage,
  });

  const AuthState.initial()
    : status = AuthStatus.initial,
      user = null,
      accessToken = null,
      refreshToken = null,
      errorMessage = null;

  const AuthState.loading()
    : status = AuthStatus.loading,
      user = null,
      accessToken = null,
      refreshToken = null,
      errorMessage = null;

  const AuthState.authenticated({
    required User user,
    required String accessToken,
    required String refreshToken,
  }) : status = AuthStatus.authenticated,
       user = user,
       accessToken = accessToken,
       refreshToken = refreshToken,
       errorMessage = null;

  const AuthState.unauthenticated()
    : status = AuthStatus.unauthenticated,
      user = null,
      accessToken = null,
      refreshToken = null,
      errorMessage = null;

  const AuthState.error(String errorMessage)
    : status = AuthStatus.error,
      user = null,
      accessToken = null,
      refreshToken = null,
      errorMessage = errorMessage;

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
  bool get hasError => status == AuthStatus.error;

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? accessToken,
    String? refreshToken,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthState &&
        other.status == status &&
        other.user == user &&
        other.accessToken == accessToken &&
        other.refreshToken == refreshToken &&
        other.errorMessage == errorMessage;
  }

  @override
  int get hashCode {
    return Object.hash(status, user, accessToken, refreshToken, errorMessage);
  }

  @override
  String toString() {
    return 'AuthState(status: $status, user: $user, accessToken: [HIDDEN], refreshToken: [HIDDEN], errorMessage: $errorMessage)';
  }
}
