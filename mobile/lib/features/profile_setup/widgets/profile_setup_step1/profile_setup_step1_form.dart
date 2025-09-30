import 'dart:io';

import 'package:flutter/material.dart';
import '../../models/profile_setup_model.dart';
import 'first_name_field.dart';
import 'last_name_field.dart';
import 'introduction_field.dart';
import 'phone_number_field.dart';
import 'social_contact_field.dart';

class ProfileSetupStep1Form extends StatelessWidget {
  final ProfileSetupModel state;
  final bool isDisabled;
  final Future<void> Function() onPickImage;

  const ProfileSetupStep1Form({
    required this.state,
    required this.isDisabled,
    required this.onPickImage,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Profile Image
        Center(
          child: GestureDetector(
            onTap: isDisabled ? null : onPickImage,
            child: Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.grey[300],
                image: state.profileImagePath != null
                    ? DecorationImage(
                        image: FileImage(File(state.profileImagePath!)),
                        fit: BoxFit.cover,
                      )
                    : null,
              ),
              child: state.profileImagePath == null
                  ? const Icon(Icons.camera_alt, size: 40, color: Colors.white)
                  : Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.black.withAlpha(30),
                      ),
                      child: const Icon(
                        Icons.camera_alt,
                        size: 30,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
        ),
        const SizedBox(height: 28),
        // First Name & Last Name
        Row(
          children: const [
            Expanded(child: FirstNameField()),
            SizedBox(width: 28),
            Expanded(child: LastNameField()),
          ],
        ),
        const SizedBox(height: 28),
        const IntroductionField(),
        const SizedBox(height: 28),
        const PhoneNumberField(),
        const SizedBox(height: 28),
        const SocialContactField(),
      ],
    );
  }
}
