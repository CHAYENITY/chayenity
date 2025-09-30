import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class FirstNameField extends ConsumerWidget {
  const FirstNameField({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('ชื่อ', style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.firstName,
          decoration: const InputDecoration(hintText: 'เอโดวาวะ'),
          onChanged: isDisabled
              ? null
              : (value) => ref
                    .read(profileSetupProvider.notifier)
                    .updateBasicInfo(firstName: value),
          enabled: !isDisabled,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'กรุณากรอกชื่อ';
            }
            return null;
          },
        ),
      ],
    );
  }
}
