import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/features/profile_setup/models/profile_setup_model.dart';
import 'package:hourz/features/profile_setup/providers/profile_setup_provider.dart';

/// ตัวอย่างการใช้งาน Profile Setup API
///
/// API Endpoint: PUT /api/auth/profile-setup
/// Authorization: Bearer Token จาก login response
///
/// การใช้งาน:
/// 1. เรียก updateBasicInfo() เพื่อกรอกข้อมูลส่วนตัว
/// 2. เรียก updateAddress() เพื่อกรอกข้อมูลที่อยู่
/// 3. เรียก submitProfile() เพื่อส่งข้อมูลไปยัง backend

/// ตัวอย่างการใช้งานในหน้า Step 1
class ProfileSetupStep1Example {
  final WidgetRef ref;

  ProfileSetupStep1Example(this.ref);

  void setupBasicInfo() {
    final notifier = ref.read(profileSetupProvider.notifier);

    // อัพเดทข้อมูลพื้นฐาน
    notifier.updateBasicInfo(
      firstName: 'string',
      lastName: 'string',
      bio: 'string',
      phoneNumber: '0816636141',
      additionalContact: 'string',
    );

    // อัพเดท profile image URL (optional)
    // notifier.updateProfileImage('path/to/local/image.jpg');

    // ไปขั้นตอนถัดไป
    notifier.completeStep1();
  }
}

/// ตัวอย่างการใช้งานในหน้า Step 2
class ProfileSetupStep2Example {
  final WidgetRef ref;

  ProfileSetupStep2Example(this.ref);

  void setupAddress() {
    final notifier = ref.read(profileSetupProvider.notifier);

    // อัพเดทข้อมูลที่อยู่
    notifier.updateAddress(
      addressText: 'string',
      district: 'string',
      province: 'string',
      postalCode: '90110',
      country: 'Thailand',
      latitude: 7.0089,
      longitude: 100.4747,
    );

    // ไปขั้นตอนถัดไป
    notifier.completeStep2();
  }
}

/// ตัวอย่างการ Submit ข้อมูลทั้งหมด
class ProfileSetupSubmitExample {
  final WidgetRef ref;

  ProfileSetupSubmitExample(this.ref);

  Future<void> submitProfileData() async {
    final notifier = ref.read(profileSetupProvider.notifier);

    // ตรวจสอบว่าข้อมูลครบหรือยัง
    final state = ref.read(profileSetupProvider);
    if (!state.canProceedToStep2) {
      print('กรุณากรอกข้อมูลพื้นฐานให้ครบ');
      return;
    }

    if (!state.canProceedToStep3) {
      print('กรุณากรอกข้อมูลที่อยู่ให้ครบ');
      return;
    }

    // Submit ข้อมูล
    try {
      final success = await notifier.submitProfile();
      if (success) {
        print('✅ Profile setup สำเร็จ!');
        // Navigate to home or success page
      } else {
        print('❌ เกิดข้อผิดพลาดในการ setup profile');
      }
    } catch (e) {
      print('❌ Error: $e');
    }
  }
}

/// ตัวอย่าง JSON ที่จะส่งไปยัง API
///
/// {
///   "first_name": "string",
///   "last_name": "string",
///   "bio": "string",
///   "phone_number": "0816636141",
///   "additional_contact": "string",
///   "profile_image_url": "string",  // optional
///   "address": {
///     "address_text": "string",
///     "district": "string",
///     "province": "string",
///     "postal_code": "string",
///     "country": "Thailand",
///     "latitude": 0,
///     "longitude": 0
///   }
/// }
///
/// Response จะได้:
/// {
///   "email": "art123123@gmail.com",
///   "first_name": "string",
///   "last_name": "string",
///   "bio": "string",
///   "phone_number": "0816636141",
///   "additional_contact": "string",
///   "is_profile_setup": true,
///   "id": "55e20bac-cbca-4cc5-a0b9-6e25eba70571",
///   "profile_image_url": "string",
///   "is_verified": false,
///   "reputation_score": 5,
///   "created_at": "2025-10-02T01:32:11.510746",
///   "addresses": []
/// }

/// ตัวอย่างการสร้าง ProfileSetupModel แบบ manual
ProfileSetupModel createProfileSetupManually() {
  return ProfileSetupModel(
    firstName: 'string',
    lastName: 'string',
    bio: 'string',
    phoneNumber: '0816636141',
    additionalContact: 'string',
    profileImageUrl: 'string',
    address: AddressModel(
      addressText: 'string',
      district: 'string',
      province: 'string',
      postalCode: 'string',
      country: 'Thailand',
      latitude: 0,
      longitude: 0,
    ),
  );
}

/// ตัวอย่างการแปลงเป็น JSON สำหรับส่ง API
void convertToApiJson() {
  final profile = createProfileSetupManually();
  final json = profile.toApiJson();

  print('JSON to send to API:');
  print(json);

  // Output:
  // {
  //   "first_name": "string",
  //   "last_name": "string",
  //   "bio": "string",
  //   "phone_number": "0816636141",
  //   "additional_contact": "string",
  //   "profile_image_url": "string",
  //   "address": {
  //     "address_text": "string",
  //     "district": "string",
  //     "province": "string",
  //     "postal_code": "string",
  //     "country": "Thailand",
  //     "latitude": 0.0,
  //     "longitude": 0.0
  //   }
  // }
}
