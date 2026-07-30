import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app/app.dart';
import 'core/config/app_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    debugPrint('[FLUTTER ERROR] ${details.exceptionAsString()}');
    debugPrintStack(stackTrace: details.stack);
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('[ASYNC ERROR] $error');
    debugPrintStack(stackTrace: stack);
    return true;
  };

  debugPrint('[APP] ${AppConfig.connectionSummary}');
  runApp(const ProviderScope(child: CoreStrengthApp()));
}
