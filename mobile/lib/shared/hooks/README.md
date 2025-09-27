# 🚀 API Service & Query Hooks Documentation (Updated for API Response Format)

## Overview

ระบบ API Service และ Query Hooks ที่สร้างขึ้นเพื่อจัดการการเรียก API ใน Flutter app ด้วย Riverpod แบบ best practice รองรับ standardized API response format

## 📁 File Structure

```
lib/shared/
├── models/
│   └── api.dart                 # API response models
├── services/
│   └── api_service.dart         # Core API service
├── hooks/
│   ├── use_query.dart          # Query hooks & providers
│   ├── example_usage.dart      # ตัวอย่างการใช้งาน
│   └── README.md               # Documentation
└── constants/
    └── api_endpoints.dart      # API endpoints
```

## 🔧 Features

### ApiService

- ✅ Generic CRUD operations (GET, POST, PUT, PATCH, DELETE)
- ✅ **Standardized API response handling**
- ✅ **Pagination support with metadata**
- ✅ Custom endpoints support
- ✅ Error handling & retry mechanism
- ✅ Request/Response logging
- ✅ Authentication token management
- ✅ Timeout configuration
- ✅ **API success/error validation**

### Query Hooks

- ✅ Type-safe query states
- ✅ **Paginated query support**
- ✅ Loading & error states
- ✅ Automatic refetch capabilities
- ✅ **Pagination controls (page, search, sort)**
- ✅ Mutation states with success tracking
- ✅ Easy-to-use helper functions
- ✅ Riverpod integration

## 📦 API Response Format

### Standard Response (Single Item)

```json
{
  "data": T | null,
  "message": "Success" | "Error message",
  "success": true | false
}
```

### Paginated Response (List)

```json
{
  "data": T[],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 10,
    "totalPages": 10
  },
  "message": "Success" | "Error message",
  "success": true | false
}
```

## 🎯 Quick Start

### 1. Basic Usage

```dart
// 📋 Get paginated list of entities
final usersProvider = useEntityList<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  pagination: const PaginationParams(limit: 10),
);

// 📄 Get entity by ID
final userProvider = useEntityById<User>(
  ApiEndpoints.users,
  userId,
  fromJson: User.fromJson,
);

// ➕ Create entity
final createUserProvider = useCreateEntity<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
);
```

### 2. In Widget

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersState = ref.watch(usersProvider);

    if (usersState.isLoading) {
      return CircularProgressIndicator();
    }

    if (usersState.hasError) {
      return Text('Error: ${usersState.error}');
    }

    return Column(
      children: [
        // List
        Expanded(
          child: ListView.builder(
            itemCount: usersState.data?.length ?? 0,
            itemBuilder: (context, index) {
              final user = usersState.data![index];
              return ListTile(
                title: Text(user.name),
                subtitle: Text(user.email),
              );
            },
          ),
        ),

        // Pagination info
        if (usersState.meta != null)
          Text('Page ${usersState.meta!.page} of ${usersState.meta!.totalPages}'),
      ],
    );
  }
}
```

### 3. Mutations

```dart
// Create
await ref.read(createUserProvider.notifier).mutate({
  'name': 'John Doe',
  'email': 'john@example.com',
});

// Update
await ref.read(updateUserProvider.notifier).mutate(userId, {
  'name': 'Jane Doe',
});

// Delete
await ref.read(deleteUserProvider.notifier).mutate(userId);
```

### 4. Pagination Controls

```dart
final usersNotifier = ref.read(usersListProvider.notifier);

// Load specific page
usersNotifier.loadPage(2);

// Search
usersNotifier.search('john');

// Sort
usersNotifier.sort('name', 'asc');

// Refresh
usersNotifier.refresh();
```

## 📚 API Reference

### useEntityList<T>() **[UPDATED]**

```dart
StateNotifierProvider<EntityListNotifier<T>, PaginatedQueryState<T>>
useEntityList<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  PaginationParams? pagination,  // NEW
  String? name,
})
```

### PaginationParams

```dart
class PaginationParams {
  final int? page;
  final int? limit;
  final String? search;
  final String? sortBy;
  final String? sortOrder; // 'asc' | 'desc'
}
```

### useEntityById<T>()

```dart
StateNotifierProvider<EntityByIdNotifier<T>, QueryState<T>>
useEntityById<T>(
  String endpoint,
  dynamic id, {
  T Function(Map<String, dynamic>)? fromJson,
  Map<String, dynamic>? queryParameters,
  String? name,
})
```

### useCreateEntity<T>()

```dart
StateNotifierProvider<CreateMutationNotifier<T>, MutationState<T>>
useCreateEntity<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
})
```

### useUpdateEntity<T>()

```dart
StateNotifierProvider<UpdateMutationNotifier<T>, MutationState<T>>
useUpdateEntity<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
})
```

### useDeleteEntity()

```dart
StateNotifierProvider<DeleteMutationNotifier, MutationState<bool>>
useDeleteEntity(
  String endpoint, {
  String? name,
})
```

### useCustomQuery<T>()

```dart
StateNotifierProvider<CustomQueryNotifier<T>, QueryState<T>>
useCustomQuery<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  Map<String, dynamic>? queryParameters,
  String? name,
})
```

### useCustomMutation<T>()

```dart
StateNotifierProvider<CustomMutationNotifier<T>, MutationState<T>>
useCustomMutation<T>(
  String endpoint, {
  T Function(Map<String, dynamic>)? fromJson,
  String? name,
})
```

## 🔄 State Management

### QueryState<T>

```dart
class QueryState<T> {
  final T? data;            // ข้อมูลจาก response.data
  final bool isLoading;     // สถานะการโหลด
  final String? error;      // ข้อความผิดพลาด
  final bool hasError;      // มีข้อผิดพลาดหรือไม่
}
```

### PaginatedQueryState<T> **[NEW]**

```dart
class PaginatedQueryState<T> {
  final List<T>? data;         // รายการข้อมูลจาก response.data
  final PaginationMeta? meta;  // ข้อมูล pagination
  final bool isLoading;        // สถานะการโหลด
  final String? error;         // ข้อความผิดพลาด
  final bool hasError;         // มีข้อผิดพลาดหรือไม่
}
```

### MutationState<T>

```dart
class MutationState<T> {
  final T? data;            // ข้อมูลจาก response.data
  final bool isLoading;     // สถานะการโหลด
  final String? error;      // ข้อความผิดพลาด
  final bool hasError;      // มีข้อผิดพลาดหรือไม่
  final bool isSuccess;     // response.success
}
```

### PaginationMeta **[NEW]**

```dart
class PaginationMeta {
  final int total;          // จำนวนข้อมูลทั้งหมด
  final int page;           // หน้าปัจจุบัน
  final int limit;          // จำนวนข้อมูลต่อหน้า
  final int totalPages;     // จำนวนหน้าทั้งหมด
}
```

## 🎨 Best Practices

### 1. Model Definition

```dart
class User {
  final int id;
  final String name;
  final String email;

  User({required this.id, required this.name, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      name: json['name'] as String,
      email: json['email'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
    };
  }
}
```

### 2. Provider Creation

```dart
// สร้าง providers ใน file แยก
final usersListProvider = useEntityList<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  pagination: const PaginationParams(limit: 10),
  name: 'UsersListProvider',
);

final createUserProvider = useCreateEntity<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  name: 'CreateUserProvider',
);
```

### 3. Error Handling **[UPDATED]**

```dart
if (state.hasError) {
  return Column(
    children: [
      Text('Error: ${state.error}'),
      ElevatedButton(
        onPressed: () => ref.read(provider.notifier).refresh(),
        child: Text('Retry'),
      ),
    ],
  );
}
```

### 4. Success Handling **[UPDATED]**

```dart
// สำหรับ mutation - ตรวจสอบ response.success
if (mutationState.isSuccess) {
  // Handle success
  ref.read(listProvider.notifier).refresh(); // Refresh list
  ref.read(mutationProvider.notifier).reset(); // Reset state
}

if (mutationState.hasError) {
  // Show error message
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Error: ${mutationState.error}')),
  );
}
```

### 5. Pagination UI **[NEW]**

```dart
// Pagination controls
if (state.meta != null && state.meta!.totalPages > 1) {
  Row(
    mainAxisAlignment: MainAxisAlignment.spaceBetween,
    children: [
      ElevatedButton(
        onPressed: state.meta!.page > 1
            ? () => notifier.loadPage(state.meta!.page - 1)
            : null,
        child: const Text('Previous'),
      ),
      Text('Page ${state.meta!.page} of ${state.meta!.totalPages}'),
      ElevatedButton(
        onPressed: state.meta!.page < state.meta!.totalPages
            ? () => notifier.loadPage(state.meta!.page + 1)
            : null,
        child: const Text('Next'),
      ),
    ],
  );
}
```

## 🔐 Authentication

```dart
// Set auth token
final apiService = ref.read(apiServiceProvider);
apiService.setAuthToken(token);

// Remove auth token
apiService.removeAuthToken();
```

## 🐛 Error Handling **[UPDATED]**

API Service จะ:

1. ตรวจสอบ `response.success` field
2. Throw exception ถ้า `success: false`
3. จัดการ standard HTTP errors:
   - Connection timeout
   - No internet connection
   - 401 Unauthorized
   - 403 Forbidden
   - 404 Not Found
   - 500 Server Error

## 🔍 Logging

API Service จะ log ข้อมูลต่างๆ อัตโนมัติ:

- 🚀 Request details
- ✅ Response data
- ❌ Error information
- 📊 API success/failure status

## 💡 Tips **[UPDATED]**

1. **ใช้ `PaginationParams`** สำหรับ list queries
2. **ตรวจสอบ `isSuccess`** สำหรับ mutations
3. **Reset mutation state** หลังจากใช้งานเสร็จ
4. **Refresh list** หลังจาก create/update/delete
5. **Handle loading states** สำหรับ UX ที่ดี
6. **Use fromJson** สำหรับ type safety
7. **แสดง pagination info** สำหรับ list ที่มีข้อมูลเยอะ
8. **ใช้ search/sort functions** สำหรับ UX ที่ดี

## 📝 Example Integration

ดูตัวอย่างการใช้งานแบบครบครันใน `example_usage.dart` ซึ่งรวมถึง:

- Pagination controls
- Search functionality
- Error handling
- Loading states
- Success validation
