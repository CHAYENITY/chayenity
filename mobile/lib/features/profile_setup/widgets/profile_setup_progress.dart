import 'package:flutter/material.dart';
import 'package:hourz/shared/providers/index.dart';

class ProfileSetupProgress extends StatelessWidget {
  final int currentStep;
  final int totalSteps;

  const ProfileSetupProgress({
    super.key,
    required this.currentStep,
    required this.totalSteps,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'ขั้นตอนที่ $currentStep/$totalSteps',
          style: const TextStyle(
            color: AppColors.mutedForeground,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: List.generate(totalSteps, (index) {
            final stepNumber = index + 1;
            final isActive = stepNumber == currentStep;
            final isCompleted = stepNumber < currentStep;

            return Expanded(
              child: Container(
                height: 6,
                margin: EdgeInsets.only(right: index < totalSteps - 1 ? 4 : 0),
                decoration: BoxDecoration(
                  color: isActive || isCompleted
                      ? AppColors.primary
                      : AppColors.muted,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }
}
