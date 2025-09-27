// ========== ตัวอย่างการใช้งาน Query Hooks (Updated for API Response Format) ==========

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:chayenity/shared/hooks/use_query.dart';
import 'package:chayenity/shared/constants/api_endpoints.dart';
import 'package:chayenity/shared/models/api.dart';

// ========== 1. Example Model ==========
class User {
  final int id;
  final String name;
  final String email;
  final DateTime? createdAt;

  User({
    required this.id,
    required this.name,
    required this.email,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      name: json['name'] as String,
      email: json['email'] as String,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'created_at': createdAt?.toIso8601String(),
    };
  }
}

// ========== 2. Providers สำหรับ Users ==========

/// Provider สำหรับดึงรายการผู้ใช้ทั้งหมด (with pagination)
final usersListProvider = useEntityList<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  pagination: const PaginationParams(limit: 10),
  name: 'UsersListProvider',
);

/// Provider สำหรับดึงผู้ใช้ตาม ID (ต้องส่ง ID เข้าไป)
StateNotifierProvider<EntityByIdNotifier<User>, QueryState<User>>
userByIdProvider(int userId) {
  return useEntityById<User>(
    ApiEndpoints.users,
    userId,
    fromJson: User.fromJson,
    name: 'UserByIdProvider_$userId',
  );
}

/// Provider สำหรับสร้างผู้ใช้ใหม่
final createUserProvider = useCreateEntity<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  name: 'CreateUserProvider',
);

/// Provider สำหรับอัปเดตผู้ใช้
final updateUserProvider = useUpdateEntity<User>(
  ApiEndpoints.users,
  fromJson: User.fromJson,
  name: 'UpdateUserProvider',
);

/// Provider สำหรับลบผู้ใช้
final deleteUserProvider = useDeleteEntity(
  ApiEndpoints.users,
  name: 'DeleteUserProvider',
);

/// Provider สำหรับดึงข้อมูลผู้ใช้ปัจจุบัน (Custom endpoint)
final currentUserProvider = useCustomQuery<User>(
  ApiEndpoints.currentUser,
  fromJson: User.fromJson,
  name: 'CurrentUserProvider',
);

// ========== 3. Example Usage in Widget ==========

class UsersListPage extends ConsumerWidget {
  const UsersListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 📖 ดึงข้อมูลรายการผู้ใช้ (with pagination)
    final usersState = ref.watch(usersListProvider);
    
    // 🔄 สำหรับ refresh ข้อมูล
    final usersNotifier = ref.read(usersListProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Users'),
        actions: [
          IconButton(
            onPressed: () => usersNotifier.refresh(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search users...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onSubmitted: (value) {
                if (value.isNotEmpty) {
                  usersNotifier.search(value);
                } else {
                  usersNotifier.refresh();
                }
              },
            ),
          ),
          
          // Content
          Expanded(
            child: usersState.isLoading
                ? const Center(child: CircularProgressIndicator())
                : usersState.hasError
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('Error: ${usersState.error}'),
                            ElevatedButton(
                              onPressed: () => usersNotifier.refresh(),
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : Column(
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
                                  trailing: IconButton(
                                    icon: const Icon(Icons.edit),
                                    onPressed: () => _showEditUserDialog(context, ref, user),
                                  ),
                                );
                              },
                            ),
                          ),
                          
                          // Pagination info
                          if (usersState.meta != null)
                            Container(
                              padding: const EdgeInsets.all(16.0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    'Page ${usersState.meta!.page} of ${usersState.meta!.totalPages}',
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                  Text(
                                    'Total: ${usersState.meta!.total}',
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ),
                          
                          // Pagination controls
                          if (usersState.meta != null && usersState.meta!.totalPages > 1)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 16.0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  ElevatedButton(
                                    onPressed: usersState.meta!.page > 1
                                        ? () => usersNotifier.loadPage(usersState.meta!.page - 1)
                                        : null,
                                    child: const Text('Previous'),
                                  ),
                                  ElevatedButton(
                                    onPressed: usersState.meta!.page < usersState.meta!.totalPages
                                        ? () => usersNotifier.loadPage(usersState.meta!.page + 1)
                                        : null,
                                    child: const Text('Next'),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showCreateUserDialog(context, ref),
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showCreateUserDialog(BuildContext context, WidgetRef ref) {
    final nameController = TextEditingController();
    final emailController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create User'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Name'),
            ),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          Consumer(
            builder: (context, ref, child) {
              final createState = ref.watch(createUserProvider);
              final createNotifier = ref.read(createUserProvider.notifier);

              return ElevatedButton(
                onPressed: createState.isLoading
                    ? null
                    : () async {
                        await createNotifier.mutate({
                          'name': nameController.text,
                          'email': emailController.text,
                        });

                        if (createState.isSuccess) {
                          Navigator.pop(context);
                          // Refresh the users list
                          ref.read(usersListProvider.notifier).refresh();
                          createNotifier.reset();
                        }
                        
                        if (createState.hasError) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Error: ${createState.error}')),
                          );
                        }
                      },
                child: createState.isLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Create'),
              );
            },
          ),
        ],
      ),
    );
  }

  void _showEditUserDialog(BuildContext context, WidgetRef ref, User user) {
    final nameController = TextEditingController(text: user.name);
    final emailController = TextEditingController(text: user.email);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit User'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Name'),
            ),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          Consumer(
            builder: (context, ref, child) {
              final updateState = ref.watch(updateUserProvider);
              final updateNotifier = ref.read(updateUserProvider.notifier);
              final deleteState = ref.watch(deleteUserProvider);
              final deleteNotifier = ref.read(deleteUserProvider.notifier);

              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Delete button
                  TextButton(
                    onPressed: deleteState.isLoading
                        ? null
                        : () async {
                            await deleteNotifier.mutate(user.id);
                            if (deleteState.isSuccess) {
                              Navigator.pop(context);
                              ref.read(usersListProvider.notifier).refresh();
                              deleteNotifier.reset();
                            }
                            
                            if (deleteState.hasError) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: ${deleteState.error}')),
                              );
                            }
                          },
                    child: deleteState.isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Delete', style: TextStyle(color: Colors.red)),
                  ),
                  // Update button
                  ElevatedButton(
                    onPressed: updateState.isLoading
                        ? null
                        : () async {
                            await updateNotifier.mutate(user.id, {
                              'name': nameController.text,
                              'email': emailController.text,
                            });

                            if (updateState.isSuccess) {
                              Navigator.pop(context);
                              ref.read(usersListProvider.notifier).refresh();
                              updateNotifier.reset();
                            }
                            
                            if (updateState.hasError) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: ${updateState.error}')),
                              );
                            }
                          },
                    child: updateState.isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Update'),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

// ========== 4. Example Usage with Custom Queries ==========

class UserProfilePage extends ConsumerWidget {
  const UserProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 📖 ดึงข้อมูลผู้ใช้ปัจจุบัน
    final currentUserState = ref.watch(currentUserProvider);
    final currentUserNotifier = ref.read(currentUserProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            onPressed: () => currentUserNotifier.refresh(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: currentUserState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : currentUserState.hasError
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Error: ${currentUserState.error}'),
                      ElevatedButton(
                        onPressed: () => currentUserNotifier.refresh(),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : currentUserState.data != null
                  ? Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Name: ${currentUserState.data!.name}',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Email: ${currentUserState.data!.email}',
                            style: Theme.of(context).textTheme.bodyLarge,
                          ),
                          const SizedBox(height: 8),
                          if (currentUserState.data!.createdAt != null)
                            Text(
                              'Created: ${currentUserState.data!.createdAt!.toString()}',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                        ],
                      ),
                    )
                  : const Center(child: Text('No data')),
    );
  }
}

// ========== 5. Usage Summary (Updated) ==========

/*
✨ สรุปการใช้งานแบบใหม่ (รองรับ API Response Format):

1. 📋 ดึงรายการข้อมูล (List) with Pagination:
   final usersState = ref.watch(usersListProvider);
   // usersState.data = List<User>
   // usersState.meta = PaginationMeta (total, page, limit, totalPages)
   
2. 📄 ดึงข้อมูลตาม ID:
   final userState = ref.watch(userByIdProvider(userId));
   // userState.data = User?
   
3. ➕ สร้างข้อมูลใหม่:
   final createState = ref.watch(createUserProvider);
   await ref.read(createUserProvider.notifier).mutate(data);
   // createState.isSuccess = response.success
   
4. ✏️ อัปเดตข้อมูล:
   final updateState = ref.watch(updateUserProvider);
   await ref.read(updateUserProvider.notifier).mutate(id, data);
   // updateState.isSuccess = response.success
   
5. 🗑️ ลบข้อมูล:
   final deleteState = ref.watch(deleteUserProvider);
   await ref.read(deleteUserProvider.notifier).mutate(id);
   // deleteState.isSuccess = response.success
   
6. 🔧 Custom Query:
   final customState = ref.watch(customQueryProvider);
   // customState.data = response.data
   
7. 🔄 Pagination Controls:
   ref.read(usersListProvider.notifier).loadPage(2);
   ref.read(usersListProvider.notifier).search('query');
   ref.read(usersListProvider.notifier).sort('name', 'asc');
   
8. ♻️ Reset mutation state:
   ref.read(mutationProvider.notifier).reset();

🎯 Updated State Properties:
- data: ข้อมูลจาก response.data
- meta: ข้อมูล pagination (สำหรับ list queries)
- isLoading: สถานะการโหลด
- hasError: มีข้อผิดพลาดหรือไม่
- error: ข้อความผิดพลาด
- isSuccess: response.success (สำหรับ mutation)

📦 API Response Structure:
{
  "data": T | T[] | null,
  "message": "Success" | "Error message",
  "success": true | false,
  "meta": { // สำหรับ paginated responses
    "total": number,
    "page": number,
    "limit": number,
    "totalPages": number
  }
}
*/