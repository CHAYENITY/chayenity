import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/login_request.dart';
import '../providers/auth_providers.dart';

class LoginFormState {
  final String email;
  final String password;
  final bool isPasswordVisible;
  final bool isFormValid;
  final String? emailError;
  final String? passwordError;

  const LoginFormState({
    this.email = '',
    this.password = '',
    this.isPasswordVisible = false,
    this.isFormValid = false,
    this.emailError,
    this.passwordError,
  });

  LoginFormState copyWith({
    String? email,
    String? password,
    bool? isPasswordVisible,
    bool? isFormValid,
    String? emailError,
    String? passwordError,
  }) {
    return LoginFormState(
      email: email ?? this.email,
      password: password ?? this.password,
      isPasswordVisible: isPasswordVisible ?? this.isPasswordVisible,
      isFormValid: isFormValid ?? this.isFormValid,
      emailError: emailError,
      passwordError: passwordError,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is LoginFormState &&
        other.email == email &&
        other.password == password &&
        other.isPasswordVisible == isPasswordVisible &&
        other.isFormValid == isFormValid &&
        other.emailError == emailError &&
        other.passwordError == passwordError;
  }

  @override
  int get hashCode {
    return Object.hash(
      email,
      password,
      isPasswordVisible,
      isFormValid,
      emailError,
      passwordError,
    );
  }
}

class LoginFormController extends StateNotifier<LoginFormState> {
  final Ref _ref;

  LoginFormController(this._ref) : super(const LoginFormState());

  void updateEmail(String email) {
    final emailError = _validateEmail(email);
    state = state.copyWith(
      email: email,
      emailError: emailError,
      isFormValid: _isFormValid(
        email,
        state.password,
        emailError,
        state.passwordError,
      ),
    );
  }

  void updatePassword(String password) {
    final passwordError = _validatePassword(password);
    state = state.copyWith(
      password: password,
      passwordError: passwordError,
      isFormValid: _isFormValid(
        state.email,
        password,
        state.emailError,
        passwordError,
      ),
    );
  }

  void togglePasswordVisibility() {
    state = state.copyWith(isPasswordVisible: !state.isPasswordVisible);
  }

  Future<void> submitForm() async {
    if (!state.isFormValid) return;

    final request = LoginRequest(
      email: state.email.trim(),
      password: state.password,
    );

    await _ref.read(authProvider.notifier).login(request);
  }

  void clearForm() {
    state = const LoginFormState();
  }

  String? _validateEmail(String email) {
    if (email.isEmpty) {
      return null; // Don't show error for empty field initially
    }

    if (!RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    ).hasMatch(email)) {
      return 'Please enter a valid email address';
    }

    return null;
  }

  String? _validatePassword(String password) {
    if (password.isEmpty) {
      return null; // Don't show error for empty field initially
    }

    if (password.length < 6) {
      return 'Password must be at least 6 characters';
    }

    return null;
  }

  bool _isFormValid(
    String email,
    String password,
    String? emailError,
    String? passwordError,
  ) {
    return email.isNotEmpty &&
        password.isNotEmpty &&
        emailError == null &&
        passwordError == null &&
        RegExp(
          r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        ).hasMatch(email) &&
        password.length >= 6;
  }
}

// Provider for the login form controller
final loginFormControllerProvider =
    StateNotifierProvider<LoginFormController, LoginFormState>((ref) {
      return LoginFormController(ref);
    });
