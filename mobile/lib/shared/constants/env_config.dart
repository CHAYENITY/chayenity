import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig {
  static String get serverUrl {
    final url = dotenv.env['SERVER_URL'];
    if (url == null) {
      return _throwMissingEnvError('SERVER_URL');
    }
    return url;
  }

  static String _throwMissingEnvError(String key) {
    throw Exception(
      'Missing required environment variable: $key\n'
      'Please check your .env file and make sure all env configuration values are set.\n'
      'See .env.example for reference.',
    );
  }

  static void validateConfiguration() {
    final requiredKeys = ['SERVER_URL'];

    final missingKeys = <String>[];

    for (final key in requiredKeys) {
      final value = dotenv.env[key];
      if (value == null || value.isEmpty || value.contains('your-')) {
        missingKeys.add(key);
      }
    }

    if (missingKeys.isNotEmpty) {
      throw Exception(
        'Missing or invalid env configuration:\n'
        '${missingKeys.map((key) => '- $key').join('\n')}\n\n'
        'Please update your .env file with actual Firebase values.\n'
        'See .env.example for reference instructions.',
      );
    }
  }
}
