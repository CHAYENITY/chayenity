import 'package:chayenity/shared/constants/env_config.dart';

class ApiEndpoints {
  // TODO ดึงจาก env
  static final String apiUrl = '${EnvConfig.serverUrl}/api';

  // Auth
  static final String login = '$apiUrl/auth/register';
  static final String register = '$apiUrl/auth/login';
}
