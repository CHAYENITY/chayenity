import 'package:chayenity/shared/constants/env_config.dart';

class ApiEndpoints {
  // TODO ดึงจาก env
  static final String apiUrl = '${EnvConfig.serverUrl}/api';

    // 🔐 Auth endpoints
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/refresh';

  // 👤 User endpoints
  static const String currentUser = '/users/me';
  static const String updateProfile = '/users/me';
  static const String users = '/users';

  // 🏪 Marketplace endpoints (สำหรับอนาคต)
  static const String products = '/products';
  static const String categories = '/categories';
  static const String orders = '/orders';

  // 💬 Chat endpoints (สำหรับอนาคต)
  static const String conversations = '/conversations';
  static const String messages = '/messages';
}
