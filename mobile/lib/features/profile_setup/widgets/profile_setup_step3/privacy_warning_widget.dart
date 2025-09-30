import 'package:flutter/material.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:lucide_icons/lucide_icons.dart';

class PrivacyWarningWidget extends StatelessWidget {
  const PrivacyWarningWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.destructive,
        borderRadius: BorderRadius.circular(25),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            LucideIcons.alertCircle,
            color: AppColors.destructiveForeground,
            size: 32,
          ),
          const SizedBox(width: 12),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 2),
                Text(
                  'ความเป็นส่วนตัว',
                  style: Theme.of(context).textTheme.titleMedium!.copyWith(
                    color: AppColors.destructiveForeground,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'ข้อมูลส่วนบุคคลของคุณจะถูกเก็บรักษาอย่างปลอดภัย และจะใช้เพื่อการยืนยันตัวตนเท่านั้น',
                  style: TextStyle(color: AppColors.destructiveForeground),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  copyWith(Color destructiveForeground) {}
}
