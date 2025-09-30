import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hourz/shared/theme/color_schemas.dart';

class TermsDialog extends ConsumerWidget {
  final VoidCallback? onAccept;
  final VoidCallback? onCancel;

  const TermsDialog({super.key, this.onAccept, this.onCancel});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 64),
      child: SizedBox(
        width: double.maxFinite,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'ข้อตกลงการใช้งาน',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'ปรับปรุงล่าสุด: 15 สิงหาคม 2568',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: AppColors.mutedForeground,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: onCancel ?? () => Navigator.of(context).pop(),
                    icon: const Icon(
                      Icons.close,
                      color: AppColors.mutedForeground,
                    ),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ),

            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildIntroText(),
                    const SizedBox(height: 24),
                    _buildSection('1. การใช้งานทั่วไป', [
                      _buildSubSection(
                        '1.1 เราคือใคร',
                        'Hourz คือแพลตฟอร์มที่เชื่อมคนสองกลุ่ม: "ผู้จ้าง" ที่ต้องการคนช่วยงานง่าย ๆ และ "ผู้ช่วย" ที่ต้องการหารายได้ในเวลาว่าง',
                      ),
                      _buildSubSection(
                        '1.2 การยอมรับ',
                        'การที่ท่านกดปุ่ม "ยอมรับ" หรือเข้าใช้แอปของเรา ถือว่าท่านตกลงตามข้อกำหนดทั้งหมดนี้ หากไม่เห็นด้วยกับข้อไหน ท่านจะไม่สามารถใช้ Hourz ได้',
                      ),
                    ]),
                    const SizedBox(height: 20),
                    _buildSection('2. บัญชีของท่าน (เป็นได้ทั้ง 2 บทบาท)', [
                      _buildSubSection(
                        '2.1 ข้อมูลส่วนตัว',
                        'ท่านต้องใช้ข้อมูลจริงในการลงทะเบียน และต้องเก็บรหัสผ่านเป็นความลับ หากมีคนอื่นใช้บัญชีของท่านโดยไม่ได้รับอนุญาต โปรดรีบแจ้งให้เราทราบ',
                      ),
                      _buildSubSection(
                        '2.2 บทบาทที่มีหยู่ (Dual Role)',
                        'บัญชีเดียวของท่านสามารถเป็นได้ทั้ง "ผู้จ้าง" และ "ผู้ช่วย" สลับกันไปมาได้ตลอดเวลา',
                      ),
                    ]),
                    const SizedBox(height: 20),
                    _buildSection('3. การกำจายและให้บริการ', [
                      _buildSubSection(
                        '3.1 สำหรับผู้ช่วย (Helper)',
                        'ท่านต้องตั้งค่า ตำแหน่งหลัก ที่ท่านสะดวกจะรับงาน และเปิด/ปิดสถานะ "พร้อมรับงาน" เมื่อท่านว่าง',
                      ),
                    ]),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),

            // Bottom Buttons
            Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                border: Border(
                  top: BorderSide(color: AppColors.border, width: 1),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: onCancel ?? () => Navigator.of(context).pop(),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text(
                        'ยกเลิก',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppColors.mutedForeground,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: onAccept,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        elevation: 0,
                      ),
                      child: const Text(
                        'ยอมรับ',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryForeground,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIntroText() {
    return Text(
      'ข้อตกลงเหล่านี้จะอธิบายถึงสิ่งที่ท่านและ Hourz มีความรับผิดชอบต่อกันการใช้แอปของเราหมายความว่าท่านยอมรับข้อตกลงเหล่านี้แล้ว โปรดอ่านสักครู่ก่อนเริ่มใช้งานจริง',
      style: TextStyle(fontSize: 14, color: AppColors.foreground, height: 1.5),
    );
  }

  Widget _buildSection(String title, List<Widget> content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        ...content,
      ],
    );
  }

  Widget _buildSubSection(String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(content, style: TextStyle(fontSize: 14, height: 1.5)),
        ],
      ),
    );
  }
}
