# 🤖 AI Coding Guide - Hourz Flutter

## 📋 Quick Reference

**Tech Stack:** Flutter + Riverpod + Freezed + Go Router + Dio + Lucide Icons
**Architecture:** Feature-based with shared global services  
**Pattern:** Immutable models, Type-safe navigation, Centralized error handling

---

## 🏗️ Project Structure

```
lib/
├── features/[feature_name]/
│   ├── screens/            # UI screens
│   ├── widgets/            # Feature widgets
│   ├── providers/          # State management
│   ├── services/           # API services
│   ├── models/             # Freezed models
│   ├── feature_routes.dart # Routes
│   └── index.dart          # Exports
└── shared/                 # Global shared code
    ├── providers/          # Global state (theme, loading, error)
    ├── services/           # API service
    ├── constants/          # Routes, configs
    ├── theme/              # Color schemas
    ├── routing/            # Go Router setup
    └── widgets/            # Reusable widgets
```

---

## 🎯 Core Templates

### 1. Freezed Model

```dart
@freezed
class ModelName with _$ModelName {
  const factory ModelName({
    required String id,
    required String title,
    @Default(false) bool isActive,
    required DateTime createdAt,
  }) = _ModelName;

  const ModelName._();
  factory ModelName.fromJson(Map<String, dynamic> json) => _$ModelNameFromJson(json);

  Map<String, dynamic> toCreateJson() => {'title': title, 'is_active': isActive};
  Map<String, dynamic> toUpdateJson() => {'title': title, 'is_active': isActive};
}
```

### 2. Provider Pattern

```dart
import 'package:hourz/shared/providers/index.dart'; // Always import

final modelServiceProvider = Provider<ModelService>((ref) {
  return ModelService(ref.read(apiProvider));
});

final modelListProvider = StateNotifierProvider<ModelListNotifier, List<ModelName>>((ref) {
  return ModelListNotifier(ref);
});

class ModelListNotifier extends StateNotifier<List<ModelName>> {
  ModelListNotifier(this._ref) : super([]);
  final Ref _ref;

  Future<void> loadData() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('load-data');
      final service = _ref.read(modelServiceProvider);
      state = await service.getItems();
    } catch (e) {
      _ref.read(errorProvider.notifier).handleError('Failed: $e', context: 'loadData');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('load-data');
    }
  }
}

// ⚡ Use .select() for computed values (no rebuild unless value changes)
final activeCountProvider = Provider<int>((ref) {
  return ref.watch(modelListProvider.select((models) =>
    models.where((m) => m.isActive).length
  ));
});

final totalCountProvider = Provider<int>((ref) {
  return ref.watch(modelListProvider.select((models) => models.length));
});
```

### 3. Service Pattern

```dart
import 'package:hourz/shared/constants/api_endpoints.dart'; // Always import

class ModelService {
  final ApiService _apiService;

  ModelService(this._apiService);

  Future<List<ModelName>> getItems() async {
    return await _apiService.getList(ApiEndpoints.models, ModelName.fromJson);
  }

  Future<ModelName> createItem(ModelName item) async {
    return await _apiService.create(ApiEndpoints.models, item.toCreateJson(), ModelName.fromJson);
  }
}
```

### 4. Screen Pattern

```dart
class ModelListScreen extends ConsumerStatefulWidget {
  const ModelListScreen({super.key});

  @override
  ConsumerState<ModelListScreen> createState() => _ModelListScreenState();
}

class _ModelListScreenState extends ConsumerState<ModelListScreen> {
  @override
  void initState() {
    super.initState();
    // Load data on first build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(modelListProvider.notifier).loadData();
    });
  }

  @override
  Widget build(BuildContext context) {
    // ⚡ Use derived providers - no rebuild unless count changes
    final totalCount = ref.watch(totalCountProvider);
    final activeCount = ref.watch(activeCountProvider);
    final isLoading = ref.watch(isLoadingProvider('load-data'));

    return Scaffold(
      appBar: AppBar(title: const Text('Models')),
      body: Column(
        children: [
          // Stats - rebuilds only when counts change
          _StatsCard(totalCount: totalCount, activeCount: activeCount),

          // List - rebuilds only when list or loading changes
          Expanded(child: _ModelListView(isLoading: isLoading)),
        ],
      ),
    );
  }
}

// Separate widget for stats (rebuilds only when counts change)
class _StatsCard extends StatelessWidget {
  final int totalCount;
  final int activeCount;

  const _StatsCard({required this.totalCount, required this.activeCount});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          _StatItem(label: 'Total', value: totalCount.toString()),
          _StatItem(label: 'Active', value: activeCount.toString()),
        ],
      ),
    );
  }
}

// List view widget (rebuilds when list changes)
class _ModelListView extends ConsumerWidget {
  final bool isLoading;

  const _ModelListView({required this.isLoading});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch only the list items
    final models = ref.watch(modelListProvider);

    return ListView.builder(
      itemCount: models.length,
      itemBuilder: (context, index) => ModelCard(
        model: models[index],
        isDisabled: isLoading,
      ),
    );
  }
}

// Helper widget (no state, never rebuilds unless parent passes new data)
class _StatItem extends StatelessWidget {
  final String label;
  final String value;

  const _StatItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) => Column(
    children: [
      Text(value, style: Theme.of(context).textTheme.headlineSmall),
      Text(label),
    ],
  );
}
```

### 5. Widget Pattern

```dart
// Main feature widget (in widgets/ folder)
class ModelCard extends StatelessWidget {
  final ModelName model;
  final bool isDisabled;

  const ModelCard({super.key, required this.model, this.isDisabled = false});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: _ModelCheckbox(model: model, isDisabled: isDisabled),
        title: Text(model.title),
        trailing: _ModelMenu(model: model, isDisabled: isDisabled),
      ),
    );
  }
}

// Separate checkbox widget (rebuilds only when checkbox state changes)
class _ModelCheckbox extends ConsumerWidget {
  final ModelName model;
  final bool isDisabled;

  const _ModelCheckbox({required this.model, required this.isDisabled});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch only isActive for this specific model
    final isActive = ref.watch(
      modelListProvider.select((models) {
        final found = models.firstWhereOrNull((m) => m.id == model.id);
        return found?.isActive ?? model.isActive; // Fallback to passed value
      })
    );

    return Checkbox(
      value: isActive,
      onChanged: isDisabled ? null : (_) =>
        ref.read(modelListProvider.notifier).toggleItem(model.id),
    );
  }
}

// Menu widget (static, no state)
class _ModelMenu extends ConsumerWidget {
  final ModelName model;
  final bool isDisabled;

  const _ModelMenu({required this.model, required this.isDisabled});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PopupMenuButton(
      enabled: !isDisabled,
      itemBuilder: (context) => [
        PopupMenuItem(
          child: const Text('Edit'),
          onTap: () => _handleEdit(ref),
        ),
        PopupMenuItem(
          child: const Text('Delete'),
          onTap: () => _handleDelete(ref),
        ),
      ],
    );
  }

  void _handleEdit(WidgetRef ref) {
    ref.read(modelListProvider.notifier).editItem(model.id);
  }

  void _handleDelete(WidgetRef ref) {
    ref.read(modelListProvider.notifier).deleteItem(model.id);
  }
}
```

### 6. Routes Pattern

```dart
import 'package:hourz/shared/constants/app_routes.dart'; // Always import

final featureRoutes = [
  GoRoute(
    path: AppRoutePath.models,
    name: AppRouteName.models,
    builder: (context, state) => const ModelListScreen(),
  ),
  GoRoute(
    path: AppRoutePath.modelDetail,
    builder: (context, state) => DetailScreen(id: state.pathParameters['id']!),
  ),
];
```

---

## 🚨 Essential Rules

### ✅ Always Do

- Use `@freezed` for all models
- Import `shared/providers/index.dart` in providers
- Handle loading/error with `loadingProvider` & `errorProvider`
- Use `.select()` when watching specific values
- Use `ref.read()` for actions (onClick, onSubmit)
- Use GoRouter: `context.go()`, `context.push()`, `context.pop()`

### ❌ Never Do

- Use `Navigator.push()` (use GoRouter)
- Mutate Freezed objects directly
- Use `ref.watch()` inside callbacks
- Skip error/loading handling
- Watch entire providers when you need only one field

---

## ⚡ Performance Rules

### 1. Use `.select()` for Partial State

```dart
// ❌ Rebuilds on ANY change
final user = ref.watch(userProvider);

// ✅ Rebuilds only when name changes
final name = ref.watch(userProvider.select((u) => u.name));
```

### 2. Separate Widgets by State

```dart
// ❌ Entire Column rebuilds
Column([
  Text(ref.watch(dataProvider)),
  if (ref.watch(loadingProvider)) CircularProgressIndicator(),
])

// ✅ Only indicator rebuilds
Column([
  const _DataText(),
  const _LoadingIndicator(),
])
```

### 3. Cache Computed Values

```dart
// Create derived provider
final activeCountProvider = Provider<int>((ref) =>
  ref.watch(itemsProvider.select((items) =>
    items.where((i) => i.isActive).length
  ))
);
```

### 4. Widget Organization

- **Reusable/Complex** → `widgets/` folder (e.g., `ModelCard`)
- **Simple/Private** → `_Widget` in screen (e.g., `_StatItem`)
- **Use `const`** wherever possible
- **Separate** `ConsumerWidget` for frequently changing parts

---

> 💡 **Pro Tip:** ดูตัวอย่างเพิ่มเติมที่โฟลเดอร์ `_example`
