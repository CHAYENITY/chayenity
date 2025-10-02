import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../models/index.dart';

/// 🎴 Gig Card Widget - แสดงข้อมูล gig ในรูปแบบ card
class GigCard extends ConsumerWidget {
  final Gig gig;
  final VoidCallback? onTap;

  const GigCard({super.key, required this.gig, this.onTap});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // รูปภาพพร้อม distance badge
            Stack(
              children: [
                AspectRatio(
                  aspectRatio: 16 / 9,
                  child: gig.imageUrl.isNotEmpty
                      ? Image.network(
                          gig.imageUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              color: Colors.grey.shade200,
                              child: const Icon(
                                Icons.image_not_supported,
                                size: 48,
                                color: Colors.grey,
                              ),
                            );
                          },
                        )
                      : Container(
                          color: Colors.grey.shade200,
                          child: const Icon(
                            Icons.image,
                            size: 48,
                            color: Colors.grey,
                          ),
                        ),
                ),

                // ระยะทาง badge
                if (gig.distance > 0)
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        gig.distanceText,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
              ],
            ),

            // ข้อมูล
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // หมวดหมู่
                  Text(
                    gig.category,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 4),

                  // ชื่อ
                  Text(
                    gig.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),

                  // ราคา
                  Text(
                    gig.priceRange,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 🏷️ Category Tab Widget
class CategoryTab extends ConsumerWidget {
  final Category? category; // null = "ทั้งหมด"
  final bool isSelected;
  final VoidCallback onTap;

  const CategoryTab({
    super.key,
    this.category,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final displayName = category?.name ?? 'ทั้งหมด';

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 0),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : AppColors.muted,
          borderRadius: BorderRadius.circular(25),
        ),
        alignment: Alignment.center,
        child: Text(
          displayName,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: isSelected
                ? AppColors.primaryForeground
                : AppColors.mutedForeground,
          ),
        ),
      ),
    );
  }
}

/// 🔍 Custom Search Bar Widget
class CustomSearchBar extends ConsumerStatefulWidget {
  final String hint;
  final VoidCallback? onFilterTap;

  const CustomSearchBar({
    super.key,
    this.hint = 'ค้นหาผู้ช่วยงานจากชื่อหรืองานที่คุณสนใจ',
    this.onFilterTap,
  });

  @override
  ConsumerState<CustomSearchBar> createState() => _CustomSearchBarState();
}

class _CustomSearchBarState extends ConsumerState<CustomSearchBar> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Search field
        Expanded(
          child: Container(
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(25),
            ),
            alignment: Alignment.center,
            child: TextField(
              controller: _controller,
              textAlignVertical: TextAlignVertical.center,
              decoration: InputDecoration(
                hintText: widget.hint,
                hintStyle: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: AppColors.mutedForeground,
                  letterSpacing: 0,
                ),
                prefixIcon: Icon(
                  LucideIcons.search,
                  color: AppColors.mutedForeground,
                  size: 20,
                ),
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 0,
                ),
                isCollapsed: true,
              ),
              onChanged: (value) {
                // Update search query in provider
                // This will be implemented later
              },
            ),
          ),
        ),

        const SizedBox(width: 12),

        // Filter button
        if (widget.onFilterTap != null) ...[
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primary,
              shape: BoxShape.circle,
            ),
            child: IconButton(
              icon: const Icon(
                LucideIcons.filter,
                color: AppColors.primaryForeground,
                size: 20,
              ),
              onPressed: () {
                widget.onFilterTap;
              },
            ),
          ),
        ],
      ],
    );
  }
}
