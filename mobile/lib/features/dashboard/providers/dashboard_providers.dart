import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import '../models/index.dart';
import '../services/dashboard_service.dart';

/// Dashboard Service Provider
final dashboardServiceProvider = Provider<DashboardService>((ref) {
  final apiService = ref.read(apiProvider);
  return DashboardService(apiService);
});

/// Gigs List State Notifier
class GigsListNotifier extends StateNotifier<List<Gig>> {
  GigsListNotifier(this._ref) : super([]);
  final Ref _ref;

  Future<void> loadGigs() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('load-gigs');
      final service = _ref.read(dashboardServiceProvider);
      final gigs = await service.getGigs();
      state = gigs;
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError('ไม่สามารถโหลดข้อมูลงานได้: $e', context: 'loadGigs');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('load-gigs');
    }
  }

  Future<void> refreshGigs() async {
    await loadGigs();
  }
}

/// Categories List State Notifier
class CategoriesListNotifier extends StateNotifier<List<Category>> {
  CategoriesListNotifier(this._ref) : super([]);
  final Ref _ref;

  Future<void> loadCategories() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('load-categories');
      final service = _ref.read(dashboardServiceProvider);
      final categories = await service.getCategories();
      state = categories;
    } catch (e) {
      _ref
          .read(errorProvider.notifier)
          .handleError(
            'ไม่สามารถโหลดหมวดหมู่ได้: $e',
            context: 'loadCategories',
          );
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('load-categories');
    }
  }
}

/// Selected Category State
class SelectedCategoryNotifier extends StateNotifier<String?> {
  SelectedCategoryNotifier() : super(null);

  void selectCategory(String? categoryId) {
    state = categoryId;
  }

  void clearCategory() {
    state = null;
  }
}

/// Search Query State
class SearchQueryNotifier extends StateNotifier<String> {
  SearchQueryNotifier() : super('');

  void updateQuery(String query) {
    state = query;
  }

  void clearQuery() {
    state = '';
  }
}

/// Providers
final gigsListProvider = StateNotifierProvider<GigsListNotifier, List<Gig>>(
  (ref) => GigsListNotifier(ref),
);

final categoriesListProvider =
    StateNotifierProvider<CategoriesListNotifier, List<Category>>(
      (ref) => CategoriesListNotifier(ref),
    );

final selectedCategoryProvider =
    StateNotifierProvider<SelectedCategoryNotifier, String?>(
      (ref) => SelectedCategoryNotifier(),
    );

final searchQueryProvider = StateNotifierProvider<SearchQueryNotifier, String>(
  (ref) => SearchQueryNotifier(),
);

/// Filtered Gigs Provider - กรองตาม category และ search
final filteredGigsProvider = Provider<List<Gig>>((ref) {
  final gigs = ref.watch(gigsListProvider);
  final selectedCategory = ref.watch(selectedCategoryProvider);
  final searchQuery = ref.watch(searchQueryProvider);

  var filtered = gigs;

  // Filter by category
  if (selectedCategory != null && selectedCategory.isNotEmpty) {
    filtered = filtered
        .where((gig) => gig.category == selectedCategory)
        .toList();
  }

  // Filter by search query
  if (searchQuery.isNotEmpty) {
    final query = searchQuery.toLowerCase();
    filtered = filtered
        .where(
          (gig) =>
              gig.title.toLowerCase().contains(query) ||
              gig.description.toLowerCase().contains(query),
        )
        .toList();
  }

  return filtered;
});

/// Loading States
final isGigsLoadingProvider = Provider<bool>((ref) {
  return ref.watch(isLoadingProvider('load-gigs'));
});

final isCategoriesLoadingProvider = Provider<bool>((ref) {
  return ref.watch(isLoadingProvider('load-categories'));
});
