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
```

### 3. Service Pattern

```dart
class ModelService {
  final ApiService _apiService;
  static const String _endpoint = '/models';

  ModelService(this._apiService);

  Future<List<ModelName>> getItems() async {
    return await _apiService.getList(_endpoint, ModelName.fromJson);
  }

  Future<ModelName> createItem(ModelName item) async {
    return await _apiService.create(_endpoint, item.toCreateJson(), ModelName.fromJson);
  }
}
```

### 4. Screen Pattern

```dart
class ModelListScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState<ModelListScreen> createState() => _ModelListScreenState();
}

class _ModelListScreenState extends ConsumerState<ModelListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(modelListProvider.notifier).loadData();
    });
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(modelListProvider);
    final isLoading = ref.watch(isLoadingProvider('load-data'));

    return Scaffold(
      appBar: AppBar(title: const Text('Models')),
      body: Column(
        children: [
          // Stats card with private widget
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                _StatItem(label: 'Total', value: data.length.toString()),
                _StatItem(label: 'Active', value: '${data.where((m) => m.isActive).length}'),
              ],
            ),
          ),

          // List with feature widget
          Expanded(
            child: ListView.builder(
              itemCount: data.length,
              itemBuilder: (context, index) => ModelCard(
                model: data[index],
                isDisabled: isLoading,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

### 5. Widget Pattern

```dart
// Main feature widget (in widgets/ folder)
class ModelCard extends ConsumerWidget {
  final ModelName model;
  final bool isDisabled;

  const ModelCard({super.key, required this.model, this.isDisabled = false});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: ListTile(
        leading: Checkbox(
          value: model.isActive,
          onChanged: isDisabled ? null : (_) => _handleToggle(ref),
        ),
        title: Text(model.title),
        trailing: PopupMenuButton(/* menu items */),
      ),
    );
  }

  void _handleToggle(WidgetRef ref) {
    ref.read(modelListProvider.notifier).toggleItem(model.id);
  }
}

// Private helper widgets (in same screen file)
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

### 6. Routes Pattern

```dart
final featureRoutes = [
  GoRoute(
    path: '/models',
    builder: (context, state) => const ModelListScreen(),
  ),
  GoRoute(
    path: '/models/:id',
    builder: (context, state) => DetailScreen(id: state.pathParameters['id']!),
  ),
];
```

---

## 🚨 Essential Rules

**✅ Always:** Use `@freezed`, import `shared/providers/index.dart`, handle loading/error  
**❌ Never:** Use `Navigator` (use GoRouter), mutate Freezed objects, skip error handling

**Widget Guidelines:**

- Complex/reusable components → `widgets/` folder (e.g., `ModelCard`)
- Simple helper widgets → private `_Widget` in same screen file (e.g., `_StatItem`)
- Use `ConsumerWidget` for widgets that need state

**Navigation:** `context.go('/path')`, `context.push('/path')`, `context.pop()`  
**Code Gen:** `generate-code.bat` (Windows) or `./generate-code.sh` (Linux)

---

---

## ⚡️ Performance Optimization (Flutter UI)

**Tips for efficient UI and AI code generation:**

- ใช้ `const` widget ให้มากที่สุด เพื่อลดการ rebuild
- แยก `ConsumerWidget` เฉพาะจุดที่ state เปลี่ยนบ่อย (เช่น field ในฟอร์ม)
- หลีกเลี่ยงการ rebuild ทั้งหน้าจอหรือ column ใหญ่ ๆ
- ใช้ provider/selector เฉพาะ field ถ้า state management รองรับ
- Optimize ภาพ: resize ก่อนแสดง, ใช้ cache ถ้าจำเป็น

ใช้แนวทางนี้เมื่อสร้างหรือปรับ UI เพื่อให้โค้ดมีประสิทธิภาพสูงสุด

หากต้องการดูรายละเอียดเพิ่มเติม ให้ดูที่โฟลเดอร์ `_example`
