import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/custom_status_bar.dart';
import '../providers/profile_setup_provider.dart';
import '../widgets/profile_setup_progress.dart';
import '../widgets/profile_setup_step3/index.dart';

class ProfileSetupStep3Screen extends ConsumerStatefulWidget {
  const ProfileSetupStep3Screen({super.key});

  @override
  ConsumerState<ProfileSetupStep3Screen> createState() =>
      _ProfileSetupStep3ScreenState();
}

class _ProfileSetupStep3ScreenState
    extends ConsumerState<ProfileSetupStep3Screen> {
  bool _hasUploadedImage = false;

  @override
  void initState() {
    super.initState();
    // Initialize with current state
    final state = ref.read(profileSetupProvider);
    _hasUploadedImage = state.citizenIdImagePath != null;
  }

  void _handleImagePicked() {
    setState(() {
      _hasUploadedImage = true;
    });
  }

  Future<void> _handleSubmit() async {
    if (!_hasUploadedImage) {
      ref
          .read(errorProvider.notifier)
          .handleError(
            'กรุณาอัปโหลดรูป Citizen ID ก่อน',
            context: 'submitProfile',
          );
      return;
    }

    final success = await ref
        .read(profileSetupProvider.notifier)
        .submitProfile();

    if (success) {
      ref.read(profileSetupProvider.notifier).completeStep3();

      // Show success dialog
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            title: const Text('สำเร็จ!'),
            content: const Text('การตั้งค่าโปรไฟล์เสร็จสมบูรณ์แล้ว'),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  context.go('/home'); // Navigate to home or appropriate screen
                },
                child: const Text('ตกลง'),
              ),
            ],
          ),
        );
      }
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
                          currentStep: 3,
                          totalSteps: 3,
                        ),

                        const SizedBox(height: 36),

                        // Header
                        const Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'อัพโหลดบัตรประจำตัวประชาชน',
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
                            'ยืนยันตัวตนด้วย Citizen ID ของคุณ',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),

                        const SizedBox(height: 28),

                        // Profile Setup Form
                        ProfileSetupStep3Form(
                          state: state,
                          isDisabled: isLoading,
                          onImagePicked: _handleImagePicked,
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
                          onPressed: (isLoading || !_hasUploadedImage)
                              ? null
                              : _handleSubmit,
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
                                  'เสร็จสิ้น',
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
