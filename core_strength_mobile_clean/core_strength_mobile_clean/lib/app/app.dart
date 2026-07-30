import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/config/app_config.dart';
import '../core/theme/app_theme.dart';
import '../core/widgets/responsive_app_frame.dart';
import '../features/auth/domain/entities/app_user.dart';
import '../features/auth/presentation/pages/login_page.dart';
import '../features/auth/presentation/pages/splash_page.dart';
import '../features/auth/presentation/providers/auth_provider.dart';
import '../features/gym/presentation/pages/member_shell.dart';
import '../features/gym/presentation/pages/trainer_shell.dart';
import 'realtime_sync_listener.dart';

class CoreStrengthApp extends StatelessWidget {
  const CoreStrengthApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: AppConfig.appName,
      theme: AppTheme.light,
      builder: (context, child) => ResponsiveAppFrame(child: child ?? const SizedBox.shrink()),
      home: const AppGate(),
    );
  }
}

class AppGate extends ConsumerStatefulWidget {
  const AppGate({super.key});

  @override
  ConsumerState<AppGate> createState() => _AppGateState();
}

class _AppGateState extends ConsumerState<AppGate> {
  @override
  void initState() {
    super.initState();
    Future.microtask(ref.read(authControllerProvider.notifier).restoreSession);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);
    return switch (state.status) {
      AuthStatus.initial || AuthStatus.restoring => const SplashPage(),
      AuthStatus.authenticated => RealtimeSyncListener(
          user: state.user!,
          child: state.user?.role == UserRole.trainer
              ? TrainerShell(user: state.user!)
              : MemberShell(user: state.user!),
        ),
      // Quan trọng: khi đang gửi form, vẫn giữ LoginPage trên cây widget.
      // Bản cũ chuyển sang SplashPage làm listener lỗi bị hủy nên không hiện lỗi.
      AuthStatus.unauthenticated ||
      AuthStatus.submitting ||
      AuthStatus.failure =>
        const LoginPage(),
    };
  }
}
