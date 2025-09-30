import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class IntroductionField extends ConsumerWidget {
  const IntroductionField({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('แนะนำตัวเอง', style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.introduction,
          decoration: const InputDecoration(
            hintText: 'ชอบช่วยเหลือเรื่องสัตว์เลี้ยงและงานสวน',
          ),
          onChanged: isDisabled
              ? null
              : (value) => ref
                    .read(profileSetupProvider.notifier)
                    .updateBasicInfo(introduction: value),
          enabled: !isDisabled,
        ),
      ],
    );
  }
}
