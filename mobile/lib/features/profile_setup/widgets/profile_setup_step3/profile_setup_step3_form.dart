import 'package:flutter/material.dart';
import '../../models/profile_setup_model.dart';
import 'citizen_id_upload_widget.dart';
import 'privacy_warning_widget.dart';

class ProfileSetupStep3Form extends StatelessWidget {
  final ProfileSetupModel state;
  final bool isDisabled;
  final VoidCallback onImagePicked;

  const ProfileSetupStep3Form({
    required this.state,
    required this.isDisabled,
    required this.onImagePicked,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Citizen ID Upload
        CitizenIdUploadWidget(
          citizenIdImagePath: state.citizenIdImagePath,
          hasUploadedImage: state.citizenIdImagePath != null,
          onImagePicked: onImagePicked,
        ),

        const SizedBox(height: 30),

        // Privacy Warning
        const PrivacyWarningWidget(),
      ],
    );
  }
}
