import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

// Auth Service Provider
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref.read(apiProvider));
});

// Current User Provider
final currentUserProvider = StateProvider<User?>((ref) => null);

// Auth State Provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref);
});

// Login Form Provider
final loginFormProvider =
    StateNotifierProvider<LoginFormNotifier, LoginFormState>((ref) {
      return LoginFormNotifier(ref);
    });

// Register Form Provider
final registerFormProvider =
    StateNotifierProvider<RegisterFormNotifier, RegisterFormState>((ref) {
      return RegisterFormNotifier(ref);
    });

// Auth State
enum AuthStatus { initial, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? error;

  const AuthState({this.status = AuthStatus.initial, this.user, this.error});

  AuthState copyWith({AuthStatus? status, User? user, String? error}) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error ?? this.error,
    );
  }
}

// Auth Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final Ref _ref;

  AuthNotifier(this._ref) : super(const AuthState());

  Future<bool> login(String email, String password) async {
    try {
      print('🟡 [LOGIN] Starting login for: $email');
      state = state.copyWith(status: AuthStatus.loading);
      _ref.read(loadingProvider.notifier).startLoading('auth-login');

      final request = LoginRequest(email: email, password: password);
      final service = _ref.read(authServiceProvider);
      final loginResponse = await service.login(request);

      print('🟢 [LOGIN] Login successful! Access token received');
      print('🔵 [LOGIN] is_profile_setup: ${loginResponse.isProfileSetup}');
      print('🔵 [LOGIN] Fetching user profile...');

      // Store tokens in secure storage
      final storageService = _ref.read(storageServiceProvider);
      await storageService.saveAccessToken(loginResponse.accessToken);
      await storageService.saveRefreshToken(loginResponse.refreshToken);

      // Set access token for API calls
      final apiService = _ref.read(apiProvider);
      apiService.setAuthToken(loginResponse.accessToken);

      final user = await service.getCurrentUser();

      print('🟢 [LOGIN] User profile loaded: ${user.email}');
      _ref.read(currentUserProvider.notifier).state = user;
      state = state.copyWith(status: AuthStatus.authenticated, user: user);

      return loginResponse.isProfileSetup;
    } catch (e) {
      print('🔴 [LOGIN] Error: $e');
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      _ref
          .read(errorProvider.notifier)
          .handleError('Login failed: $e', context: 'auth-login');
      return false;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-login');
      print('🟡 [LOGIN] Finished');
    }
  }

  Future<bool> register(
    String email,
    String password,
    String confirmPassword,
  ) async {
    try {
      state = state.copyWith(status: AuthStatus.loading);
      _ref.read(loadingProvider.notifier).startLoading('auth-register');

      final request = RegisterRequest(
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );
      if (!request.isPasswordMatch) {
        throw Exception('รหัสผ่านไม่ตรงกัน');
      }

      final service = _ref.read(authServiceProvider);
      final user = await service.register(request);

      _ref.read(currentUserProvider.notifier).state = user;
      state = state.copyWith(status: AuthStatus.authenticated, user: user);
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      _ref
          .read(errorProvider.notifier)
          .handleError('Register failed: $e', context: 'auth-register');
      return false;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-register');
    }
  }

  Future<void> logout() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('auth-logout');
      final service = _ref.read(authServiceProvider);
      await service.logout();

      // Clear stored tokens
      final storageService = _ref.read(storageServiceProvider);
      await storageService.clearAllTokens();

      // Clear API auth token
      final apiService = _ref.read(apiProvider);
      apiService.clearAuthToken();

      _ref.read(currentUserProvider.notifier).state = null;
      state = state.copyWith(status: AuthStatus.unauthenticated, user: null);
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('Logout failed: $e', context: 'auth-logout');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-logout');
    }
  }

  /// Check authentication status on app startup
  /// Returns the route to navigate to based on auth status
  Future<String?> checkAuthStatus() async {
    try {
      print('🟡 [AUTH_CHECK] Checking authentication status...');
      state = state.copyWith(status: AuthStatus.loading);

      final storageService = _ref.read(storageServiceProvider);
      final apiService = _ref.read(apiProvider);
      final service = _ref.read(authServiceProvider);

      // Check if refresh token exists
      final refreshToken = await storageService.getRefreshToken();
      if (refreshToken == null) {
        print('🔴 [AUTH_CHECK] No refresh token found');
        state = state.copyWith(status: AuthStatus.unauthenticated);
        return null; // Will navigate to login
      }

      print('🟢 [AUTH_CHECK] Refresh token found');

      // Try to get access token and fetch user profile
      final accessToken = await storageService.getAccessToken();
      if (accessToken != null) {
        print('🔵 [AUTH_CHECK] Access token found, checking user profile...');
        apiService.setAuthToken(accessToken);

        try {
          final user = await service.getCurrentUser();
          print('🟢 [AUTH_CHECK] User profile loaded: ${user.email}');
          _ref.read(currentUserProvider.notifier).state = user;
          state = state.copyWith(status: AuthStatus.authenticated, user: user);

          // Check profile setup status
          if (user.isProfileSetup) {
            print('🟢 [AUTH_CHECK] Profile is set up, navigating to dashboard');
            return 'dashboard';
          } else {
            print(
              '🟡 [AUTH_CHECK] Profile not set up, navigating to profile setup',
            );
            return 'profileSetup';
          }
        } catch (e) {
          print('🔴 [AUTH_CHECK] Failed to fetch user with access token: $e');
          print('🔵 [AUTH_CHECK] Attempting to refresh token...');
        }
      }

      // If we get here, either no access token or it failed
      // Try to refresh the access token
      try {
        final oldAccessToken = accessToken ?? '';
        final refreshResponse = await service.refreshToken(
          refreshToken,
          oldAccessToken,
        );

        print('🟢 [AUTH_CHECK] Token refreshed successfully');

        // Save new access token
        await storageService.saveAccessToken(refreshResponse.accessToken);
        apiService.setAuthToken(refreshResponse.accessToken);

        // Fetch user profile with new token
        final user = await service.getCurrentUser();
        print(
          '🟢 [AUTH_CHECK] User profile loaded after refresh: ${user.email}',
        );
        _ref.read(currentUserProvider.notifier).state = user;
        state = state.copyWith(status: AuthStatus.authenticated, user: user);

        // Check profile setup status
        if (user.isProfileSetup) {
          print('🟢 [AUTH_CHECK] Profile is set up, navigating to dashboard');
          return 'dashboard';
        } else {
          print(
            '🟡 [AUTH_CHECK] Profile not set up, navigating to profile setup',
          );
          return 'profileSetup';
        }
      } catch (e) {
        print('🔴 [AUTH_CHECK] Token refresh failed: $e');
        // Clear invalid tokens
        await storageService.clearAllTokens();
        apiService.clearAuthToken();
        state = state.copyWith(status: AuthStatus.unauthenticated);
        return null; // Will navigate to login
      }
    } catch (e) {
      print('🔴 [AUTH_CHECK] Unexpected error: $e');
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      return null; // Will navigate to login
    }
  }

  Future<void> loginWithGoogle() async {
    try {
      state = state.copyWith(status: AuthStatus.loading);
      _ref.read(loadingProvider.notifier).startLoading('auth-google');

      final service = _ref.read(authServiceProvider);
      await service.loginWithGoogle();

      // TODO: Handle Google login response
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      _ref
          .read(errorProvider.notifier)
          .handleError('Google login failed: $e', context: 'auth-google');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-google');
    }
  }
}

// Login Form State
class LoginFormState {
  final String email;
  final String password;
  final bool obscurePassword;

  const LoginFormState({
    this.email = '',
    this.password = '',
    this.obscurePassword = true,
  });

  LoginFormState copyWith({
    String? email,
    String? password,
    bool? obscurePassword,
  }) {
    return LoginFormState(
      email: email ?? this.email,
      password: password ?? this.password,
      obscurePassword: obscurePassword ?? this.obscurePassword,
    );
  }

  bool get isValid => email.isNotEmpty && password.isNotEmpty;
}

// Login Form Notifier
class LoginFormNotifier extends StateNotifier<LoginFormState> {
  final Ref _ref;

  LoginFormNotifier(this._ref) : super(const LoginFormState());

  void setEmail(String email) {
    state = state.copyWith(email: email);
  }

  void setPassword(String password) {
    state = state.copyWith(password: password);
  }

  void togglePasswordVisibility() {
    state = state.copyWith(obscurePassword: !state.obscurePassword);
  }

  Future<bool> submit() async {
    if (!state.isValid) return false;
    return await _ref
        .read(authProvider.notifier)
        .login(state.email, state.password);
  }
}

// Register Form State
class RegisterFormState {
  final String email;
  final String password;
  final String confirmPassword;
  final bool obscurePassword;
  final bool obscureConfirmPassword;
  final bool agreeToTerms;

  const RegisterFormState({
    this.email = '',
    this.password = '',
    this.confirmPassword = '',
    this.obscurePassword = true,
    this.obscureConfirmPassword = true,
    this.agreeToTerms = false,
  });

  RegisterFormState copyWith({
    String? email,
    String? password,
    String? confirmPassword,
    bool? obscurePassword,
    bool? obscureConfirmPassword,
    bool? agreeToTerms,
  }) {
    return RegisterFormState(
      email: email ?? this.email,
      password: password ?? this.password,
      confirmPassword: confirmPassword ?? this.confirmPassword,
      obscurePassword: obscurePassword ?? this.obscurePassword,
      obscureConfirmPassword:
          obscureConfirmPassword ?? this.obscureConfirmPassword,
      agreeToTerms: agreeToTerms ?? this.agreeToTerms,
    );
  }

  bool get isValid =>
      email.isNotEmpty &&
      password.isNotEmpty &&
      confirmPassword.isNotEmpty &&
      password == confirmPassword &&
      agreeToTerms;
  bool get isPasswordMatch => password == confirmPassword;
}

// Register Form Notifier
class RegisterFormNotifier extends StateNotifier<RegisterFormState> {
  final Ref _ref;

  RegisterFormNotifier(this._ref) : super(const RegisterFormState());

  void setEmail(String email) {
    state = state.copyWith(email: email);
  }

  void setPassword(String password) {
    state = state.copyWith(password: password);
  }

  void setConfirmPassword(String confirmPassword) {
    state = state.copyWith(confirmPassword: confirmPassword);
  }

  void togglePasswordVisibility() {
    state = state.copyWith(obscurePassword: !state.obscurePassword);
  }

  void toggleConfirmPasswordVisibility() {
    state = state.copyWith(
      obscureConfirmPassword: !state.obscureConfirmPassword,
    );
  }

  void setAgreeToTerms(bool agree) {
    state = state.copyWith(agreeToTerms: agree);
  }

  Future<bool> submit() async {
    if (!state.isValid) return false;
    return await _ref
        .read(authProvider.notifier)
        .register(state.email, state.password, state.confirmPassword);
  }
}
