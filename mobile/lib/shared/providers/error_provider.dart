import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/models/api.dart';

/// Error State Model
class ErrorState {
  final String message;
  final String? code;
  final DateTime timestamp;
  final String? context;

  ErrorState({
    required this.message,
    this.code,
    required this.timestamp,
    this.context,
  });
}

/// Global Error Handler
class ErrorHandler extends StateNotifier<ErrorState?> {
  ErrorHandler() : super(null);

  /// Handle API errors
  void handleApiError(ApiException error, {String? context}) {
    state = ErrorState(
      message: error.message,
      code: error.statusCode?.toString(),
      timestamp: DateTime.now(),
      context: context,
    );
  }

  /// Handle general errors
  void handleError(String message, {String? code, String? context}) {
    state = ErrorState(
      message: message,
      code: code,
      timestamp: DateTime.now(),
      context: context,
    );
  }

  /// Clear error
  void clearError() {
    state = null;
  }
}

/// Global Error Provider
final errorProvider = StateNotifierProvider<ErrorHandler, ErrorState?>(
  (ref) => ErrorHandler(),
);

/// Helper provider to check if there's an error
final hasErrorProvider = Provider<bool>((ref) {
  return ref.watch(errorProvider) != null;
});
