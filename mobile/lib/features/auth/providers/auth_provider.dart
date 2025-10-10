import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/features/auth/models/auth.dart';
import 'package:hourz/features/auth/services/auth_service.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:logger/logger.dart';

// ============================================================================
// Auth Service Provider
// ============================================================================

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref.read(apiProvider));
});

// ============================================================================
// Login Form State
// ============================================================================

@immutable
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

  bool get isValid =>
      email.isNotEmpty &&
      email.contains('@') &&
      password.isNotEmpty &&
      password.length >= 8;
}

// ============================================================================
// Login Form Provider
// ============================================================================

final loginFormProvider =
    StateNotifierProvider<LoginFormNotifier, LoginFormState>((ref) {
      return LoginFormNotifier(ref);
    });

class LoginFormNotifier extends StateNotifier<LoginFormState> {
  final Ref _ref;
  final Logger _logger = Logger();

  LoginFormNotifier(this._ref) : super(const LoginFormState());

  void setEmail(String email) {
    state = state.copyWith(email: email.trim().toLowerCase());
  }

  void setPassword(String password) {
    state = state.copyWith(password: password);
  }

  void togglePasswordVisibility() {
    state = state.copyWith(obscurePassword: !state.obscurePassword);
  }

  /// Submit login form
  /// Returns true if user profile is already setup
  Future<bool> submit() async {
    if (!state.isValid) {
      _logger.w('⚠️ Login form is invalid');
      return false;
    }

    try {
      _ref.read(loadingProvider.notifier).startLoading('auth-login');

      final request = LoginRequest(
        email: state.email,
        password: state.password,
      );

      final authService = _ref.read(authServiceProvider);
      final token = await authService.login(request);

      // Save token to secure storage
      await _ref.read(tokenProvider.notifier).saveToken(token);

      _logger.d('✅ Login successful');

      // TODO: Check if user profile is setup (implement later)
      // For now, assume profile is setup
      return true;
    } catch (e) {
      _logger.e('❌ Login failed: $e');
      _ref
          .read(errorProvider.notifier)
          .handleError(
            'เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบอีเมลและรหัสผ่าน',
            context: 'login',
          );
      rethrow;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-login');
    }
  }

  void reset() {
    state = const LoginFormState();
  }
}

// ============================================================================
// Register Form State
// ============================================================================

@immutable
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

  bool get isPasswordMatch =>
      password.isNotEmpty &&
      confirmPassword.isNotEmpty &&
      password == confirmPassword;

  bool get isValid =>
      email.isNotEmpty &&
      email.contains('@') &&
      password.isNotEmpty &&
      password.length >= 8 &&
      isPasswordMatch &&
      agreeToTerms;
}

// ============================================================================
// Register Form Provider
// ============================================================================

final registerFormProvider =
    StateNotifierProvider<RegisterFormNotifier, RegisterFormState>((ref) {
      return RegisterFormNotifier(ref);
    });

class RegisterFormNotifier extends StateNotifier<RegisterFormState> {
  final Ref _ref;
  final Logger _logger = Logger();

  RegisterFormNotifier(this._ref) : super(const RegisterFormState());

  void setEmail(String email) {
    state = state.copyWith(email: email.trim().toLowerCase());
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

  /// Submit registration form
  /// Returns true if registration successful
  Future<bool> submit() async {
    if (!state.isValid) {
      _logger.w('⚠️ Register form is invalid');
      return false;
    }

    try {
      _ref.read(loadingProvider.notifier).startLoading('auth-register');

      final request = RegisterRequest(
        email: state.email,
        password: state.password,
        confirmPassword: state.confirmPassword,
      );

      final authService = _ref.read(authServiceProvider);
      await authService.register(request);

      _logger.d('✅ Registration successful');
      return true;
    } catch (e) {
      _logger.e('❌ Registration failed: $e');
      _ref
          .read(errorProvider.notifier)
          .handleError(
            'ลงทะเบียนไม่สำเร็จ อีเมลนี้อาจถูกใช้งานแล้ว',
            context: 'register',
          );
      rethrow;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-register');
    }
  }

  void reset() {
    state = const RegisterFormState();
  }
}

// ============================================================================
// Auth State Provider (For Google Sign In & General Auth)
// ============================================================================

final authProvider = StateNotifierProvider<AuthNotifier, AsyncValue<void>>(
  (ref) => AuthNotifier(ref),
);

class AuthNotifier extends StateNotifier<AsyncValue<void>> {
  final Ref _ref;
  final Logger _logger = Logger();

  AuthNotifier(this._ref) : super(const AsyncValue.data(null));

  /// Login with Google (Placeholder - implement when Google Sign In is ready)
  Future<void> loginWithGoogle() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('auth-google');
      state = const AsyncValue.loading();

      // TODO: Implement Google Sign In
      _logger.w('⚠️ Google Sign In not implemented yet');

      await Future.delayed(const Duration(seconds: 1)); // Simulate API call

      _ref
          .read(errorProvider.notifier)
          .handleError(
            'Google Sign In ยังไม่พร้อมใช้งาน',
            context: 'google-signin',
          );

      state = const AsyncValue.data(null);
    } catch (e) {
      _logger.e('❌ Google Sign In failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('auth-google');
    }
  }

  /// Logout user
  Future<void> logout() async {
    try {
      final authService = _ref.read(authServiceProvider);
      await authService.logout();
    } catch (e) {
      _logger.e('❌ Logout API failed: $e');
      // Continue logout even if API fails
    } finally {
      // Always clear local token
      await _ref.read(tokenProvider.notifier).clearToken();
      _logger.d('✅ User logged out');
    }
  }

  /// Check authentication status on app start
  /// Returns route to navigate to
  Future<String> checkAuthStatus() async {
    try {
      // Load token from secure storage
      await _ref.read(tokenProvider.notifier).loadToken();

      final isAuthenticated = _ref.read(isAuthenticatedProvider);

      if (isAuthenticated) {
        _logger.d('✅ User is authenticated');
        // TODO: Check if profile setup is complete
        // For now, go to dashboard
        return '/dashboard';
      } else {
        _logger.d('❌ User is not authenticated');
        return '/login';
      }
    } catch (e) {
      _logger.e('❌ Check auth status failed: $e');
      return '/login';
    }
  }
}
