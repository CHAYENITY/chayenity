import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/index.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../providers/index.dart';
import '../widgets/index.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // โหลดข้อมูลเมื่อเข้าหน้า
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(gigsListProvider.notifier).loadGigs();
      ref.read(categoriesListProvider.notifier).loadCategories();
    });
  }

  @override
  Widget build(BuildContext context) {
    // Watch states
    final filteredGigs = ref.watch(filteredGigsProvider);
    final categories = ref.watch(categoriesListProvider);
    final selectedCategory = ref.watch(selectedCategoryProvider);
    final isLoading = ref.watch(isGigsLoadingProvider);

    return CustomStatusBar(
      child: Scaffold(
        backgroundColor: AppColors.background,
        resizeToAvoidBottomInset: true,
        body: Stack(
          children: [
            Container(
              height: MediaQuery.of(context).size.height,
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.center,
                  colors: [AppColors.muted, AppColors.background],
                ),
              ),
              child: SafeArea(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32),
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.only(
                      bottom: 100,
                    ), // เพิ่ม padding เพื่อไม่ให้ content ทับกับ island
                    child: Column(
                      children: [
                        // Header
                        _buildHeader(),

                        const SizedBox(height: 16),

                        // Search Bar
                        CustomSearchBar(
                          onFilterTap: () {
                            // TODO: Implement filter
                          },
                        ),

                        const SizedBox(height: 16),

                        // Category Tabs
                        SizedBox(
                          height: 25,
                          child: ListView(
                            scrollDirection: Axis.horizontal,
                            children: [
                              // 'ทั้งหมด' Tab
                              CategoryTab(
                                isSelected: selectedCategory == null,
                                onTap: () {
                                  ref
                                      .read(selectedCategoryProvider.notifier)
                                      .clearCategory();
                                },
                              ),

                              const SizedBox(width: 12),

                              // Category tabs
                              ...categories.map((category) {
                                final isSelected =
                                    selectedCategory == category.id;
                                return CategoryTab(
                                  category: category,
                                  isSelected: isSelected,
                                  onTap: () {
                                    ref
                                        .read(selectedCategoryProvider.notifier)
                                        .selectCategory(category.id);
                                  },
                                );
                              }),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Loading indicator
                        if (isLoading) const LinearProgressIndicator(),

                        // Gigs Grid
                        if (filteredGigs.isEmpty && !isLoading)
                          _buildEmptyState()
                        else
                          RefreshIndicator(
                            onRefresh: () => ref
                                .read(gigsListProvider.notifier)
                                .refreshGigs(),
                            child: GridView.builder(
                              shrinkWrap: true,
                              physics: const NeverScrollableScrollPhysics(),
                              padding: const EdgeInsets.all(16),
                              gridDelegate:
                                  const SliverGridDelegateWithFixedCrossAxisCount(
                                    crossAxisCount: 2,
                                    childAspectRatio: 0.75,
                                    crossAxisSpacing: 12,
                                    mainAxisSpacing: 12,
                                  ),
                              itemCount: filteredGigs.length,
                              itemBuilder: (context, index) {
                                final gig = filteredGigs[index];
                                return GigCard(
                                  gig: gig,
                                  onTap: () {
                                    // TODO: Navigate to gig detail
                                  },
                                );
                              },
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            // Navigation Island
            const NavigationIsland(currentRoute: '/home'),
          ],
        ),
      ),
    );
  }

  /// Header Widget
  Widget _buildHeader() {
    // TODO: Replace with real username from user state/provider
    const String username = 'Edogawa Conan';
    const String city = 'หาดใหญ่';

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // Greeting and city (wraps if too long)
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'สวัสดี $username',
                style: TextStyle(
                  color: AppColors.mutedForeground,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              RichText(
                text: TextSpan(
                  style: AppTheme.richText.merge(
                    const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  children: [
                    const TextSpan(text: 'มาเริ่มการหางาน/ผู้ช่วยใน '),
                    TextSpan(
                      text: city,
                      style: TextStyle(color: AppColors.mutedForeground),
                    ),
                    const TextSpan(text: ' กัน!'),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(width: 12),

        // Bell & Avatar
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Bell icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: const Icon(
                  LucideIcons.bell,
                  color: AppColors.primaryForeground,
                  size: 24,
                ),
                onPressed: () {
                  // TODO: Navigate to notifications
                },
              ),
            ),

            const SizedBox(width: 12),

            // Avatar
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.muted,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: const Icon(
                  Icons.person,
                  color: AppColors.primary,
                  size: 24,
                ),
                onPressed: () {
                  // TODO: Navigate to profile
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// Empty State Widget
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.work_outline, size: 96, color: AppColors.muted),
          const SizedBox(height: 16),
          Text(
            'ไม่พบงาน',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.mutedForeground,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ลองค้นหาด้วยคำอื่นหรือเปลี่ยนหมวดหมู่',
            style: TextStyle(color: AppColors.mutedForeground),
          ),
        ],
      ),
    );
  }
}
