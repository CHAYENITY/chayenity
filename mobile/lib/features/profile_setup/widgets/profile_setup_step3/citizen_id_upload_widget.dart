import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'dart:io';
import 'package:hourz/shared/providers/index.dart';
import '../../providers/profile_setup_provider.dart';

class CitizenIdUploadWidget extends ConsumerStatefulWidget {
  final String? citizenIdImagePath;
  final bool hasUploadedImage;
  final VoidCallback onImagePicked;

  const CitizenIdUploadWidget({
    required this.citizenIdImagePath,
    required this.hasUploadedImage,
    required this.onImagePicked,
    super.key,
  });

  @override
  ConsumerState<CitizenIdUploadWidget> createState() =>
      _CitizenIdUploadWidgetState();
}

class _CitizenIdUploadWidgetState extends ConsumerState<CitizenIdUploadWidget> {
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickCitizenIdImage() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1200,
        maxHeight: 1200,
        imageQuality: 85,
      );

      if (image != null) {
        ref
            .read(profileSetupProvider.notifier)
            .updateCitizenIdImage(image.path);

        widget.onImagePicked();

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('อัปโหลดรูป Citizen ID เรียบร้อยแล้ว'),
              backgroundColor: Color(0xFF00B4A6),
            ),
          );
        }
      }
    } catch (e) {
      ref
          .read(errorProvider.notifier)
          .handleError(
            'Failed to pick Citizen ID image: $e',
            context: 'pickCitizenIdImage',
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _pickCitizenIdImage,
      child: Container(
        width: double.infinity,
        height: 220,
        decoration: BoxDecoration(
          border: Border.all(
            color: AppColors.mutedForeground,
            style: BorderStyle.solid,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(25),
          color: widget.hasUploadedImage
              ? AppColors.mutedForeground
              : AppColors.background,
          image: widget.citizenIdImagePath != null
              ? DecorationImage(
                  image: FileImage(File(widget.citizenIdImagePath!)),
                  fit: BoxFit.cover,
                )
              : null,
        ),
        child: widget.citizenIdImagePath == null
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    widget.hasUploadedImage
                        ? Icons.check_circle
                        : LucideIcons.upload,
                    size: 48,
                    color: widget.hasUploadedImage
                        ? AppColors.background
                        : AppColors.mutedForeground,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    widget.hasUploadedImage
                        ? 'อัปโหลดเรียบร้อยแล้ว'
                        : 'อัปโหลดรูปภาพบัตรประชาชน หรือพาสปอร์ต',
                    style: Theme.of(context).textTheme.titleMedium!.copyWith(
                      color: widget.hasUploadedImage
                          ? AppColors.background
                          : AppColors.mutedForeground,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'รองรับไฟล์ JPG, PNG ขนาดไม่เกิน 5MB',
                    style: TextStyle(color: AppColors.mutedForeground),
                    textAlign: TextAlign.center,
                  ),
                ],
              )
            : Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(25),
                  color: AppColors.mutedForeground,
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.edit, size: 30, color: AppColors.background),
                      SizedBox(height: 8),
                      Text(
                        'แตะเพื่อเปลี่ยนรูป',
                        style: TextStyle(color: AppColors.background),
                      ),
                    ],
                  ),
                ),
              ),
      ),
    );
  }
}
