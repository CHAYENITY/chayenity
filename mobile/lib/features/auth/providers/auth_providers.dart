import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/auth_state.dart';
import '../models/login_request.dart';
import '../repositories/auth_repository.dart';

// Repository provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl();
});

// Auth state notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;

  AuthNotifier(this._authRepository) : super(const AuthState.initial());

  Future<void> login(LoginRequest request) async {
    state = const AuthState.loading();

    try {
      final response = await _authRepository.login(request);
      state = AuthState.authenticated(
        user: response.user,
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );
    } catch (e) {
      state = AuthState.error(e.toString().replaceFirst('AuthException: ', ''));
    }
  }

  Future<void> logout() async {
    state = const AuthState.loading();

    try {
      await _authRepository.logout();
      state = const AuthState.unauthenticated();
    } catch (e) {
      // Even if logout fails, we should clear the local state
      state = const AuthState.unauthenticated();
    }
  }

  Future<void> refreshToken() async {
    if (state.refreshToken == null) {
      state = const AuthState.unauthenticated();
      return;
    }

    try {
      final response = await _authRepository.refreshToken(state.refreshToken!);
      state = AuthState.authenticated(
        user: response.user,
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );
    } catch (e) {
      state = const AuthState.unauthenticated();
    }
  }

  void clearError() {
    if (state.hasError) {
      state = const AuthState.unauthenticated();
    }
  }

  void initialize() {
    // In a real app, you would check for stored tokens here
    // and validate them with the server
    state = const AuthState.unauthenticated();
  }
}

// Auth state provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AuthNotifier(authRepository);
});

// Convenience providers for specific auth state properties
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isAuthenticated;
});

final isLoadingProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isLoading;
});

final currentUserProvider = Provider((ref) {
  return ref.watch(authProvider).user;
});

final authErrorProvider = Provider<String?>((ref) {
  final authState = ref.watch(authProvider);
  return authState.hasError ? authState.errorMessage : null;
});
