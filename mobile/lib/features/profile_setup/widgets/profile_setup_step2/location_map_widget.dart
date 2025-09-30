import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:location/location.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class LocationMapWidget extends ConsumerWidget {
  const LocationMapWidget({super.key});

  Future<void> _confirmCurrentLocation(
    WidgetRef ref,
    BuildContext context,
  ) async {
    final Location location = Location();

    try {
      // Check and request permission
      bool serviceEnabled = await location.serviceEnabled();
      if (!serviceEnabled) {
        serviceEnabled = await location.requestService();
        if (!serviceEnabled) {
          throw Exception('Location service is disabled');
        }
      }

      PermissionStatus permissionGranted = await location.hasPermission();
      if (permissionGranted == PermissionStatus.denied) {
        permissionGranted = await location.requestPermission();
        if (permissionGranted != PermissionStatus.granted) {
          throw Exception('Location permission denied');
        }
      }

      // Get current location
      final LocationData locationData = await location.getLocation();

      if (locationData.latitude != null && locationData.longitude != null) {
        ref
            .read(profileSetupProvider.notifier)
            .confirmCurrentLocation(
              locationData.latitude!,
              locationData.longitude!,
            );

        // Show confirmation
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('ยืนยันตำแหน่งปัจจุบันเรียบร้อยแล้ว'),
              backgroundColor: AppColors.primary,
            ),
          );
        }
      } else {
        throw Exception('Unable to get location coordinates');
      }
    } catch (e) {
      // Fallback to mock coordinates for สงขลา
      const mockLatitude = 7.0061;
      const mockLongitude = 100.4981;

      ref
          .read(profileSetupProvider.notifier)
          .confirmCurrentLocation(mockLatitude, mockLongitude);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('ใช้ตำแหน่งเริ่มต้น: $e'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));

    return Column(
      children: [
        // Map placeholder
        Container(
          height: 200,
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[300]!),
          ),
          child: Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.blue[100]!,
                        Colors.green[100]!,
                        Colors.blue[50]!,
                      ],
                    ),
                  ),
                  child: const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.map, size: 40, color: Colors.grey),
                        SizedBox(height: 8),
                        Text(
                          'แผนที่จะแสดงที่นี่',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Positioned(
                top: 50,
                left: 100,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'สงขลา',
                    style: TextStyle(color: Colors.white, fontSize: 10),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        // Confirm location button
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: isDisabled
                ? null
                : () => _confirmCurrentLocation(ref, context),
            icon: Transform.translate(
              offset: const Offset(0, -2),
              child: Transform.rotate(
                angle: -0.785398, // 45 degrees in radians
                child: const Icon(Icons.send, color: AppColors.primary),
              ),
            ),
            label: const Text(
              'ยืนยันตัวดำแหน่งปัจจุบัน',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ),
      ],
    );
  }
}
