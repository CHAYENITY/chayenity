class AppConfig {
  // App
  static const String appName = 'Hourz';
  static const String appVersion = '1.0.0';

  // Network
  static const Duration apiTimeout = Duration(seconds: 30);

  // Animation
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);

  // Local Storage Keys
  static const String userTokenKey = 'user_token';
  static const String userDataKey = 'user_data';
}
