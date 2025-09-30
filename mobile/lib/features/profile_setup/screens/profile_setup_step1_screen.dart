import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/constants/app_routes.dart';
import 'package:image_picker/image_picker.dart';
import 'package:go_router/go_router.dart';
import 'package:hourz/shared/providers/index.dart';
import 'package:hourz/shared/widgets/custom_status_bar.dart';
import '../providers/profile_setup_provider.dart';
import '../widgets/profile_setup_progress.dart';
import '../widgets/profile_setup_step1/profile_setup_step1_form.dart';

class ProfileSetupStep1Screen extends ConsumerStatefulWidget {
  const ProfileSetupStep1Screen({super.key});

  @override
  ConsumerState<ProfileSetupStep1Screen> createState() =>
      _ProfileSetupStep1ScreenState();
}

class _ProfileSetupStep1ScreenState
    extends ConsumerState<ProfileSetupStep1Screen> {
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 80,
      );
      if (image != null) {
        ref.read(profileSetupProvider.notifier).updateProfileImage(image.path);
      }
    } catch (e) {
      ref
          .read(errorProvider.notifier)
          .handleError('Failed to pick image: $e', context: 'pickImage');
    }
  }

  void _handleNext(BuildContext context) {
    final state = ref.read(profileSetupProvider);
    if (state.canProceedToStep2) {
      ref.read(profileSetupProvider.notifier).completeStep1();
      context.push(AppRoutePath.profileSetupStep2);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('กรุณากรอกข้อมูลให้ครบถ้วน'),
          backgroundColor: Colors.red,
        ),
      );
    }
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
                          currentStep: 1,
                          totalSteps: 3,
                        ),

                        const SizedBox(height: 36),

                        // Header
                        const Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'ข้อมูลพื้นฐานและรูปภาพ',
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
                            'สวัสดี Hourz User! มาเริ่มตั้งค่าโปรไฟล์กัน',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),

                        const SizedBox(height: 28),

                        // Profile Setup Form
                        ProfileSetupStep1Form(
                          state: state,
                          isDisabled: isLoading,
                          onPickImage: _pickImage,
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
                          onPressed: null,
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
                          onPressed: isLoading
                              ? null
                              : () => _handleNext(context),
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
