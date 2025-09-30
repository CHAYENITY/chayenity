import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/custom_status_bar.dart';
import '../providers/profile_setup_provider.dart';
import '../widgets/profile_setup_progress.dart';
import '../widgets/profile_setup_step2/index.dart';

class ProfileSetupStep2Screen extends ConsumerStatefulWidget {
  const ProfileSetupStep2Screen({super.key});

  @override
  ConsumerState<ProfileSetupStep2Screen> createState() =>
      _ProfileSetupStep2ScreenState();
}

class _ProfileSetupStep2ScreenState
    extends ConsumerState<ProfileSetupStep2Screen> {
  void _handleNext() {
    // Check if can proceed to step 3
    final currentState = ref.read(profileSetupProvider);
    if (currentState.canProceedToStep3) {
      // Complete step 2 and navigate to step 3
      ref.read(profileSetupProvider.notifier).completeStep2();
      context.push(AppRoutePath.profileSetupStep3);
    } else {
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('กรุณากรอกข้อมูลที่อยู่และยืนยันตำแหน่ง'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _handleBack() {
    ref.read(profileSetupProvider.notifier).previousStep();
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileSetupProvider);
    final isLoading = ref.watch(isLoadingProvider('submit-profile'));

    return CustomStatusBar(
      child: Scaffold(
        backgroundColor: AppColors.background,
        resizeToAvoidBottomInset: true,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              children: [
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        const SizedBox(height: 16),

                        // Progress indicator
                        const ProfileSetupProgress(
                          currentStep: 2,
                          totalSteps: 3,
                        ),

                        const SizedBox(height: 36),

                        // Header
                        const Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'ยืนยันตำแหน่งพื้นที่',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              color: AppColors.mutedForeground,
                            ),
                          ),
                        ),

                        const SizedBox(height: 4),

                        const Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'กำหนดพื้นที่สำหรับการใช้บริการเลย',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),

                        const SizedBox(height: 28),

                        // Profile Setup Form
                        ProfileSetupStep2Form(
                          state: state,
                          isDisabled: isLoading,
                        ),
                      ],
                    ),
                  ),
                ),

                // Buttons
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: isLoading || !Navigator.canPop(context)
                              ? null
                              : _handleBack,
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: const Text(
                            'ย้อนกลับ',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: isLoading ? null : _handleNext,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white,
                                    ),
                                  ),
                                )
                              : const Text(
                                  'ถัดไป',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
