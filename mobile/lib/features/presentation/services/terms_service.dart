import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TermsService {
  static const _acceptedKey = 'terms_accepted';

  /// บันทึกว่าเคยยอมรับ Terms แล้ว
  static Future<void> acceptTerms(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_acceptedKey, true);
    // สามารถทำ navigation ต่อไปได้ เช่นไปหน้า Home
  }

  /// ตรวจสอบว่าเคยยอมรับ Terms หรือยัง
  static Future<bool> hasAcceptedTerms() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_acceptedKey) ?? false;
  }

  /// ถ้าอยาก reset (สำหรับ debug)
  static Future<void> resetTerms() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_acceptedKey);
  }
}
