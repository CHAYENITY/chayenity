import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class SocialContactField extends ConsumerWidget {
  const SocialContactField({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ช่องทางติดต่อเพิ่มเติม',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.socialContact,
          decoration: const InputDecoration(
            hintText: 'Facebook: Hourz Official / LineID: @hourzofficial',
          ),
          onChanged: isDisabled
              ? null
              : (value) => ref
                    .read(profileSetupProvider.notifier)
                    .updateBasicInfo(socialContact: value),
          enabled: !isDisabled,
        ),
      ],
    );
  }
}
