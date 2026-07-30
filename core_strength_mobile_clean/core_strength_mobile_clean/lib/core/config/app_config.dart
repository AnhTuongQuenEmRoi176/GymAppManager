import 'package:flutter/foundation.dart';

class AppConfig {
  const AppConfig._();

  /// Sau khi backend đã được tạo, mặc định chạy API thật.
  /// Muốn dùng dữ liệu demo: --dart-define=USE_MOCK_DATA=true
  static const bool useMockData = bool.fromEnvironment(
    'USE_MOCK_DATA',
    defaultValue: false,
  );

  static const String _definedApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  static const String _definedWebSocketUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: '',
  );

  /// - Android Emulator dùng 10.0.2.2 để truy cập localhost của máy tính.
  /// - Windows/Web/iOS Simulator dùng 127.0.0.1.
  /// - Điện thoại thật bắt buộc truyền IP LAN bằng --dart-define.
  static String get apiBaseUrl {
    if (_definedApiBaseUrl.trim().isNotEmpty) {
      return _trimTrailingSlash(_definedApiBaseUrl.trim());
    }

    if (kIsWeb ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.macOS ||
        defaultTargetPlatform == TargetPlatform.linux ||
        defaultTargetPlatform == TargetPlatform.iOS) {
      return 'http://127.0.0.1:8000/api';
    }

    return 'http://10.0.2.2:8000/api';
  }

  static String get webSocketUrl {
    if (_definedWebSocketUrl.trim().isNotEmpty) {
      return _trimTrailingSlash(_definedWebSocketUrl.trim());
    }

    if (kIsWeb ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.macOS ||
        defaultTargetPlatform == TargetPlatform.linux ||
        defaultTargetPlatform == TargetPlatform.iOS) {
      return 'ws://127.0.0.1:8000/ws';
    }

    return 'ws://10.0.2.2:8000/ws';
  }


  static String get publicBaseUrl {
    final uri = Uri.parse(apiBaseUrl);
    final path = uri.path.endsWith('/api')
        ? uri.path.substring(0, uri.path.length - 4)
        : uri.path;
    return uri.replace(path: path, query: null, fragment: null).toString().replaceAll(RegExp(r'/$'), '');
  }

  static String? resolvePublicUrl(String? value) {
    final raw = value?.trim();
    if (raw == null || raw.isEmpty) return null;

    final base = Uri.parse(publicBaseUrl);
    final parsed = Uri.tryParse(raw);
    if (parsed == null) return null;

    if (!parsed.hasScheme) {
      final normalized = raw.startsWith('/') ? raw : '/$raw';
      return base.replace(path: normalized).toString();
    }

    if (parsed.host == '127.0.0.1' || parsed.host == 'localhost') {
      return parsed.replace(
        scheme: base.scheme,
        host: base.host,
        port: base.hasPort ? base.port : null,
      ).toString();
    }

    return raw;
  }

  static const String appName = 'CORE STRENGTH';
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 20);

  static String get connectionSummary => useMockData
      ? 'MOCK DATA'
      : 'API: $apiBaseUrl | WS: $webSocketUrl';

  static String _trimTrailingSlash(String value) {
    var result = value;
    while (result.endsWith('/')) {
      result = result.substring(0, result.length - 1);
    }
    return result;
  }
}
