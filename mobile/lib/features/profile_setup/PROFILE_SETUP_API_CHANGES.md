# Profile Setup API Integration

## สรุปการเปลี่ยนแปลง

เพิ่มการเรียกใช้ API endpoint: `PUT /api/auth/profile-setup`

### 1. โครงสร้างข้อมูล (Models)

#### ✅ เพิ่ม `AddressModel`

- `addressText`: ที่อยู่แบบเต็ม
- `district`: อำเภอ
- `province`: จังหวัด
- `postalCode`: รหัสไปรษณีย์
- `country`: ประเทศ (default: Thailand)
- `latitude`: ละติจูด
- `longitude`: ลองจิจูด

#### ✅ อัพเดท `ProfileSetupModel`

เปลี่ยนจาก:

- `introduction` → `bio`
- `socialContact` → `additionalContact`
- `address`, `district`, `province`, etc. → `AddressModel`

เพิ่มฟิลด์:

- `profileImageUrl`: URL รูปโปรไฟล์จาก server

### 2. API Service

#### ✅ เพิ่ม `updateProfile()` method ใน `ApiService`

```dart
Future<T> updateProfile<T>(
  String endpoint,
  Map<String, dynamic> data,
  T Function(Map<String, dynamic>) fromJson,
)
```

Method นี้เป็น PUT แบบไม่ต้องส่ง ID ใน path (สำหรับ `/auth/profile-setup`)

#### ✅ อัพเดท `ProfileSetupService`

- เปลี่ยนจาก `POST /profile-setup` เป็น `PUT /auth/profile-setup`
- ใช้ `updateProfile()` แทน `create()`
- ใช้ `toApiJson()` แทน `toCreateJson()`

### 3. State Management

#### ✅ อัพเดท `ProfileSetupProvider`

- `updateBasicInfo()`: รองรับ `bio` และ `additionalContact`
- `updateAddress()`: รองรับ `AddressModel` แบบ nested
- `confirmCurrentLocation()`: อัพเดท lat/lng ใน `AddressModel`

### 4. API Request Format

```json
{
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "phone_number": "0816636141",
  "additional_contact": "string",
  "profile_image_url": "string",
  "address": {
    "address_text": "string",
    "district": "string",
    "province": "string",
    "postal_code": "string",
    "country": "Thailand",
    "latitude": 0,
    "longitude": 0
  }
}
```

### 5. API Response Format

```json
{
  "email": "art123123@gmail.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "phone_number": "0816636141",
  "additional_contact": "string",
  "is_profile_setup": true,
  "id": "55e20bac-cbca-4cc5-a0b9-6e25eba70571",
  "profile_image_url": "string",
  "is_verified": false,
  "reputation_score": 5,
  "created_at": "2025-10-02T01:32:11.510746",
  "addresses": []
}
```

## การใช้งาน

### ตัวอย่าง 1: อัพเดทข้อมูลพื้นฐาน (Step 1)

```dart
final notifier = ref.read(profileSetupProvider.notifier);

notifier.updateBasicInfo(
  firstName: 'ชื่อ',
  lastName: 'นามสกุล',
  bio: 'แนะนำตัว',
  phoneNumber: '0816636141',
  additionalContact: 'Line: @myline',
);

notifier.completeStep1();
```

### ตัวอย่าง 2: อัพเดทข้อมูลที่อยู่ (Step 2)

```dart
final notifier = ref.read(profileSetupProvider.notifier);

notifier.updateAddress(
  addressText: '123 ถนนสุขุมวิท',
  district: 'หาดใหญ่',
  province: 'สงขลา',
  postalCode: '90110',
  country: 'Thailand',
  latitude: 7.0089,
  longitude: 100.4747,
);

notifier.completeStep2();
```

### ตัวอย่าง 3: Submit ข้อมูล

```dart
final notifier = ref.read(profileSetupProvider.notifier);
final success = await notifier.submitProfile();

if (success) {
  // Navigate to home
} else {
  // Show error
}
```

## สิ่งที่ต้องแก้ไขใน UI

### ❗ Screen และ Widget ที่ต้องอัพเดท

1. **profile_setup_step1_screen.dart**

   - เปลี่ยนชื่อฟิลด์: `introduction` → `bio`
   - เปลี่ยนชื่อฟิลด์: `socialContact` → `additionalContact`

2. **profile_setup_step1/introduction_field.dart**

   - ควรเปลี่ยนชื่อไฟล์เป็น `bio_field.dart`
   - อัพเดทการเรียกใช้ `updateBasicInfo(bio: ...)`

3. **profile_setup_step1/social_contact_field.dart**

   - ควรเปลี่ยนชื่อไฟล์เป็น `additional_contact_field.dart`
   - อัพเดทการเรียกใช้ `updateBasicInfo(additionalContact: ...)`

4. **profile_setup_step2_screen.dart**

   - อัพเดทการเรียกใช้ `updateAddress()` ให้ส่งพารามิเตอร์ที่ถูกต้อง
   - เปลี่ยนจาก `address` เป็น `addressText`
   - เพิ่ม `postalCode` และ `country`

5. **profile_setup_step2/address_field.dart**
   - อัพเดทให้ส่ง `addressText` แทน `address`

## Authorization

API นี้ต้องการ Bearer Token ใน Header:

```
Authorization: Bearer <access_token>
```

Token จะถูก set อัตโนมัติหลังจาก login สำเร็จผ่าน `AuthService.login()`

## Testing

### ตัวอย่าง curl command:

```bash
curl -X 'PUT' \
  'http://localhost:8000/api/auth/profile-setup' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'Content-Type: application/json' \
  -d '{
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "phone_number": "0816636141",
  "additional_contact": "string",
  "profile_image_url": "string",
  "address": {
    "address_text": "string",
    "district": "string",
    "province": "string",
    "postal_code": "string",
    "country": "Thailand",
    "latitude": 0,
    "longitude": 0
  }
}'
```

## ไฟล์ที่มีการเปลี่ยนแปลง

✅ แก้ไขแล้ว:

- `/mobile/lib/features/profile_setup/models/profile_setup_model.dart` - เพิ่ม AddressModel, อัพเดทโครงสร้าง
- `/mobile/lib/features/profile_setup/services/profile_setup_service.dart` - เปลี่ยนเป็น PUT request
- `/mobile/lib/features/profile_setup/providers/profile_setup_provider.dart` - รองรับ AddressModel
- `/mobile/lib/shared/services/api_service.dart` - เพิ่ม updateProfile() method

📝 สร้างใหม่:

- `/mobile/lib/features/profile_setup/USAGE_EXAMPLE.dart` - ตัวอย่างการใช้งาน

⚠️ ต้องแก้ไข (ตามรายการข้างบน):

- Screen และ Widget files ใน Step 1 และ Step 2

## Next Steps

1. ✅ Generate freezed code - เสร็จแล้ว
2. ⚠️ อัพเดท UI widgets ให้ใช้ชื่อฟิลด์ใหม่
3. ⚠️ Test การเรียก API จริง
4. ⚠️ Handle error cases
5. ⚠️ เพิ่ม loading states
