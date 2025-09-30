import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Loading State Notifier
class LoadingStateNotifier extends StateNotifier<Map<String, bool>> {
  LoadingStateNotifier() : super({});

  /// Start loading for a specific key
  void startLoading(String key) {
    state = {...state, key: true};
  }

  /// Stop loading for a specific key
  void stopLoading(String key) {
    state = {...state, key: false};
  }

  /// Check if loading for a specific key
  bool isLoading(String key) {
    return state[key] ?? false;
  }

  /// Check if any loading is active
  bool get hasAnyLoading {
    return state.values.any((loading) => loading);
  }

  /// Clear all loading states
  void clearAll() {
    state = {};
  }
}

/// Global Loading State Provider
final loadingProvider =
    StateNotifierProvider<LoadingStateNotifier, Map<String, bool>>(
      (ref) => LoadingStateNotifier(),
    );

/// Helper provider to check specific loading state
final isLoadingProvider = Provider.family<bool, String>((ref, key) {
  final loadingState = ref.watch(loadingProvider);
  return loadingState[key] ?? false;
});

/// Helper provider to check if any loading is active
final hasAnyLoadingProvider = Provider<bool>((ref) {
  final loadingState = ref.watch(loadingProvider);
  return loadingState.values.any((loading) => loading);
});
