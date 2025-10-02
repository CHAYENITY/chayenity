// API base URL helper
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_dotenv/flutter_dotenv.dart';

String getApiBaseUrl() {
  // Prefer explicit .env value if present
  final env = dotenv.env['API_BASE_URL'];
  if (env != null && env.isNotEmpty) return env;

  if (kIsWeb) return 'http://localhost:5000';
  if (Platform.isAndroid) return 'http://10.0.2.2:8000';
  if (Platform.isIOS) return 'http://localhost:8000';
  // Desktop fallback
  return 'http://localhost:8000';
}
