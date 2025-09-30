import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/profile_setup_provider.dart';
import '../../../../shared/providers/index.dart';

class ProvinceField extends ConsumerStatefulWidget {
  const ProvinceField({super.key});

  @override
  ConsumerState<ProvinceField> createState() => _ProvinceFieldState();
}

class _ProvinceFieldState extends ConsumerState<ProvinceField> {
  String? _selectedProvinceId;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileSetupProvider);
    final isDisabled = ref.watch(isLoadingProvider('submit-profile'));
    final provincesAsync = ref.watch(provincesProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('จังหวัด', style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        provincesAsync.when(
          data: (provinces) => DropdownButtonFormField<String>(
            value: _selectedProvinceId,
            decoration: const InputDecoration(hintText: 'เลือกจังหวัด'),
            items: provinces
                .map(
                  (province) => DropdownMenuItem<String>(
                    value: province['id'],
                    child: Text(province['name']!),
                  ),
                )
                .toList(),
            onChanged: isDisabled
                ? null
                : (value) {
                    setState(() {
                      _selectedProvinceId = value;
                    });
                    final selectedProvince = provinces.firstWhere(
                      (p) => p['id'] == value,
                      orElse: () => {'name': ''},
                    );
                    ref
                        .read(profileSetupProvider.notifier)
                        .updateLocation(province: selectedProvince['name']);
                  },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'กรุณาเลือกจังหวัด';
              }
              return null;
            },
          ),
          loading: () => TextFormField(
            decoration: const InputDecoration(hintText: 'กำลังโหลด...'),
            enabled: false,
          ),
          error: (error, stack) => TextFormField(
            initialValue: state.province,
            decoration: const InputDecoration(hintText: 'สงขลา'),
            onChanged: isDisabled
                ? null
                : (value) => ref
                      .read(profileSetupProvider.notifier)
                      .updateLocation(province: value),
            enabled: !isDisabled,
          ),
        ),
      ],
    );
  }
}
