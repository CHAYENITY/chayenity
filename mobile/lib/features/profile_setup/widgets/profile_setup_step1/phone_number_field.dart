import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class PhoneNumberField extends ConsumerWidget {
  const PhoneNumberField({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('เบอร์โทรศัพท์', style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.phoneNumber,
          decoration: const InputDecoration(hintText: '0XX-XXX-XXXX'),
          keyboardType: TextInputType.phone,
          onChanged: isDisabled
              ? null
              : (value) => ref
                    .read(profileSetupProvider.notifier)
                    .updateBasicInfo(phoneNumber: value),
          enabled: !isDisabled,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'กรุณากรอกเบอร์โทรศัพท์';
            }
            return null;
          },
        ),
      ],
    );
  }
}
