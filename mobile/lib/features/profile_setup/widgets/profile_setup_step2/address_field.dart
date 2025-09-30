import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class AddressField extends ConsumerWidget {
  const AddressField({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ที่อยู่ (กรอกด้วยตนเอง)',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.address,
          decoration: const InputDecoration(
            hintText: 'หมู่ 2 บล็อก 21 เมืองเบกะ จังหวัดทตโตริ ประเทศญี่ปุ่น',
          ),
          onChanged: isDisabled
              ? null
              : (value) => ref
                    .read(profileSetupProvider.notifier)
                    .updateLocation(address: value),
          enabled: !isDisabled,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'กรุณากรอกที่อยู่';
            }
            return null;
          },
        ),
      ],
    );
  }
}
