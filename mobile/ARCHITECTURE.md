# 🏗️ Flutter Architecture Overview - Hourz App

> **📖 สำหรับรายละเอียดเพิ่มเติม:** ดู [ARCHITECTURE_DETAILED.md](./ARCHITECTURE_DETAILED.md)  
> **🤖 สำหรับ AI Coding:** ดู [AI_CODING_GUIDE.md](./AI_CODING_GUIDE.md)

## 🚀 Tech Stack

**Core Technologies:**

- **Flutter SDK** - Cross-platform mobile development
- **Riverpod** - State management with dependency injection
- **Freezed** - Immutable data classes with code generation
- **Go Router** - Declarative routing and navigation
- **Dio** - HTTP client for API communication
- **JSON Annotation** - JSON serialization/deserialization

## 📁 Project Structure Overview

```
lib/
├── main.dart                    # App entry point with global providers
├── features/                    # แบ่งตามฟีเจอร์ (Feature-based Architecture)
│   ├── auth/                    # Authentication Feature
│   │   ├── screens/            # หน้าจอ Login, Register
│   │   ├── widgets/            # Widget เฉพาะ Auth
│   │   ├── providers/          # State Management
│   │   ├── services/           # API ของ Auth (Login, Register)
│   │   ├── models/             # Auth data models
│   │   └── index.dart          # Clean exports
│   └── _example/               # Examples & Learning Templates
│       ├── screens/            # Example screens (Tasks, Marketplace, Home)
│       ├── widgets/            # Reusable UI components
│       ├── providers/          # State management examples
│       ├── services/           # API ของ Example
│       ├── models/             # Data models
│       └── index.dart          # Clean exports
├── shared/                     # Global Feature - ใช้ร่วมกันทั่วทั้งแอป
│   ├── constants/              # App configuration
│   │   ├── app_config.dart     # App metadata
│   │   ├── app_routes.dart     # เก็บชื่อเส้นทาง
│   │   ├── api_endpoints.dart  # API endpoints
│   │   └── env_config.dart     # Environment variables
│   ├── models/                 # Global data models using Freezed
│   ├── screens/                # Global screens (Error, Loading, etc.)
│   ├── services/               # Global services
│   │   └── api_service.dart    # HTTP client with error handling
│   ├── providers/              # Global state management
│   │   ├── theme_provider.dart      # Light/Dark theme management
│   │   ├── loading_provider.dart    # Loading states management
│   │   ├── error_provider.dart      # Centralized error handling
│   │   └── index.dart              # Single import for all globals
│   ├── routing/                # Routing configuration
│   │   └── app_router.dart     # Central Go Router configuration
│   ├── theme/                  # App theming system
│   │   ├── app_theme.dart      # Light & Dark themes
│   │   ├── color_schemas.dart  # Color definitions
│   │   └── typography.dart     # Text styles
│   ├── utils/                  # Global utilities
│   │   └── common_utils.dart   # Date, String, Validation, Number utils
│   └── widgets/                # Global reusable widgets
```

## 🎯 Architecture Principles

### 1. **Feature-Based Architecture**

- แบ่งโค้ดตาม business features แทน technical layers
- แต่ละ feature มีความเป็นอิสระ (loosely coupled)
- ง่ายต่อการดูแล scale และ test

### 2. **Immutable State Management**

- ใช้ Freezed สำหรับ data models ทั้งหมด
- State ไม่สามารถเปลี่ยนแปลงได้ (immutable)
- ใช้ `copyWith()` สำหรับการอัปเดต

### 3. **Centralized Global Services**

- API Service, Theme, Loading, Error handling ใช้ร่วมกัน
- Single source of truth สำหรับ global state
- ง่ายต่อการ debug และ maintain

### 4. **Type-Safe Navigation**

- ใช้ Go Router กับ route constants
- การนำทางแบบ declarative
- รองรับ deep linking และ web URLs

## 📚 Feature Architecture Pattern

### Standard Feature Structure

ทุก feature จะมี structure เหมือนกันสำหรับความสม่ำเสมอ:

```
feature_name/
├── screens/           # UI Screens - หน้าจอต่างๆ
├── widgets/           # Reusable Components - Widget ที่ใช้ซ้ำได้
├── providers/         # State Management - Providers เฉพาะ feature
├── services/          # API Services - HTTP requests เฉพาะ feature
├── models/            # Data Models (Freezed classes)
├── feature_routes.dart # Go Router routes สำหรับ feature นี้
└── index.dart         # Export file สำหรับ clean imports
```

### 🎯 `_example` Feature

**Learning & Reference Templates**

- **Purpose**: ตัวอย่างการใช้งาน architecture และ best practices
- **Usage**: เป็น template และ reference สำหรับ features ใหม่
- **Structure**: ทำตาม standard pattern ข้างต้นแบบครบถ้วน

## 🌐 Global Architecture (Shared System)

**Shared System** ที่ทุก feature สามารถใช้ร่วมกัน:

```
shared/
├── providers/        # Global State Management
│   ├── theme_provider.dart      # Light/Dark theme
│   ├── loading_provider.dart    # Loading states
│   ├── error_provider.dart      # Error handling
│   └── index.dart              # Single import for all
├── services/         # Global Services
│   └── api_service.dart        # HTTP client
├── routing/          # Navigation
│   └── app_router.dart         # Go Router setup
├── constants/        # App Constants
│   ├── app_routes.dart         # Route definitions
│   └── api_endpoints.dart      # API URLs
├── theme/           # Theming System
├── utils/           # Common Utilities
├── models/          # Global Models
├── screens/         # Global Screens
└── widgets/         # Reusable Widgets
```

## ⚡ Quick Start Guide

### 1. **Essential Imports**

```dart
// Always import this first for global providers
import 'package:hourz/shared/providers/index.dart';

// For navigation
import 'package:go_router/go_router.dart';

// For models
import 'package:freezed_annotation/freezed_annotation.dart';
```

### 2. **Basic Model Structure**

```dart
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    @Default(false) bool isActive,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

### 3. **Feature Provider Pattern**

```dart
final userProvider = StateNotifierProvider<UserNotifier, List<User>>((ref) {
  return UserNotifier(ref);
});

class UserNotifier extends StateNotifier<List<User>> {
  UserNotifier(this._ref) : super([]);
  final Ref _ref;

  Future<void> loadUsers() async {
    try {
      _ref.read(loadingProvider.notifier).startLoading('users');
      final api = _ref.read(apiProvider);
      final users = await api.getList('/users', User.fromJson);
      state = users;
    } catch (e) {
      _ref.read(errorProvider.notifier).handleError('Failed to load users');
    } finally {
      _ref.read(loadingProvider.notifier).stopLoading('users');
    }
  }
}
```

### 4. **Navigation Usage**

```dart
// In widgets
context.go('/users');
context.push('/add-user');
context.pop();

// With route constants (recommended)
context.go(AppRoutePath.users);
context.pushNamed(AppRouteName.addUser);
```

## � Development Workflow

### Creating New Feature

1. **Create folder structure** following standard pattern
2. **Create models** with `@freezed` annotation
3. **Run code generation:** `scripts\windows\generate-code.bat`
4. **Create providers** following the pattern
5. **Create screens** using `ConsumerWidget`
6. **Define routes** in `feature_routes.dart`
7. **Export everything** in `index.dart`

### Working with Models

```bash
# After creating/modifying Freezed models
scripts\windows\generate-code.bat

# Or watch mode for development
dart run build_runner watch --delete-conflicting-outputs
```

## 🚨 Essential Rules

### ✅ **ALWAYS DO**

- Use `@freezed` for all data models
- Import `package:hourz/shared/providers/index.dart` for global providers
- Use `context.go()` / `context.push()` for navigation (not Navigator)
- Handle loading and error states in providers
- Follow standard feature folder structure
- Run code generation after model changes

### ❌ **NEVER DO**

- Use `Navigator.of(context)` (use Go Router instead)
- Mutate Freezed objects directly (use `copyWith()`)
- Skip error handling in providers
- Create models without Freezed annotation
- Forget to export in `index.dart` files

### 🎯 **Key Patterns**

```dart
// 1. State Management Flow
_ref.read(loadingProvider.notifier).startLoading('operation');
_ref.read(errorProvider.notifier).clearError();
// ... API call ...
_ref.read(loadingProvider.notifier).stopLoading('operation');

// 2. Navigation with Constants
context.go(AppRoutePath.targetScreen);
context.pushNamed(AppRouteName.editItem, extra: item);

// 3. Watching States in UI
final isLoading = ref.watch(isLoadingProvider('operation'));
final currentError = ref.watch(errorProvider);
```

---

**📖 Next Steps:**

- **Detailed Implementation:** [ARCHITECTURE_DETAILED.md](./ARCHITECTURE_DETAILED.md)
- **AI Coding Guide:** [AI_CODING_GUIDE.md](./AI_CODING_GUIDE.md)
- **Examples:** Check `features/_example/` folder
