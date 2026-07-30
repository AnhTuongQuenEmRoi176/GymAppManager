import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/app_config.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/realtime/realtime_service.dart';
import '../../../../core/storage/token_storage.dart';
import '../../data/datasources/auth_remote_data_source.dart';
import '../../data/repositories/mock_auth_repository.dart';
import '../../data/repositories/remote_auth_repository.dart';
import '../../domain/entities/app_user.dart';
import '../../domain/entities/auth_session.dart';
import '../../domain/repositories/auth_repository.dart';

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final apiClientProvider = Provider<ApiClient>(
  (ref) => ApiClient(tokenStorage: ref.watch(tokenStorageProvider)),
);

final realtimeServiceProvider = Provider<RealtimeService>((ref) {
  final service = RealtimeService(tokenStorage: ref.watch(tokenStorageProvider));
  ref.onDispose(() {
    unawaited(service.dispose());
  });
  return service;
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  if (AppConfig.useMockData) {
    return MockAuthRepository(storage);
  }
  return RemoteAuthRepository(
    remote: AuthRemoteDataSource(ref.watch(apiClientProvider)),
    storage: storage,
  );
});

enum AuthStatus {
  initial,
  restoring,
  unauthenticated,
  submitting,
  authenticated,
  failure,
}

class AuthState {
  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.message,
  });

  final AuthStatus status;
  final AppUser? user;
  final String? message;

  bool get isSubmitting => status == AuthStatus.submitting;

  AuthState copyWith({
    AuthStatus? status,
    AppUser? user,
    String? message,
    bool clearMessage = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      message: clearMessage ? null : message ?? this.message,
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._repository, this._realtime) : super(const AuthState());

  final AuthRepository _repository;
  final RealtimeService _realtime;

  Future<void> restoreSession() async {
    if (state.status != AuthStatus.initial) return;
    state = const AuthState(status: AuthStatus.restoring);
    try {
      final session = await _repository.restoreSession();
      if (session == null) {
        state = const AuthState(status: AuthStatus.unauthenticated);
        return;
      }
      state = AuthState(status: AuthStatus.authenticated, user: session.user);
      unawaited(_connectRealtimeSafely());
    } catch (error, stackTrace) {
      debugPrint('[AUTH] restoreSession lỗi: $error');
      debugPrintStack(stackTrace: stackTrace);
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login({
    required String username,
    required String password,
  }) async {
    if (state.isSubmitting) return;
    state = const AuthState(status: AuthStatus.submitting);

    try {
      debugPrint(
        '[AUTH] Đăng nhập. mode=${AppConfig.useMockData ? 'mock' : 'api'}, '
        'account=$username, baseUrl=${AppConfig.apiBaseUrl}',
      );
      final session = await _repository.login(
        username: username,
        password: password,
      );
      debugPrint(
        '[AUTH] Đăng nhập thành công: user=${session.user.username}, '
        'role=${session.user.role.apiValue}',
      );
      state = AuthState(status: AuthStatus.authenticated, user: session.user);
      unawaited(_connectRealtimeSafely());
    } catch (error, stackTrace) {
      debugPrint('[AUTH] Đăng nhập thất bại: $error');
      debugPrintStack(stackTrace: stackTrace);
      state = AuthState(
        status: AuthStatus.failure,
        message: error.toString(),
      );
    }
  }

  Future<void> _connectRealtimeSafely() async {
    try {
      await _realtime.connect();
      debugPrint('[WS] Đã bắt đầu kết nối realtime.');
    } catch (error, stackTrace) {
      // WebSocket lỗi không được làm đăng nhập thất bại.
      debugPrint('[WS] Không kết nối được realtime: $error');
      debugPrintStack(stackTrace: stackTrace);
    }
  }

  Future<PasswordResetRequestResult> requestPasswordReset(String account) {
    return _repository.requestPasswordReset(account);
  }

  Future<void> resetPassword({
    required String account,
    required String otp,
    required String newPassword,
  }) {
    return _repository.resetPassword(
      account: account,
      otp: otp,
      newPassword: newPassword,
    );
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) {
    return _repository.changePassword(
      currentPassword: currentPassword,
      newPassword: newPassword,
    );
  }

  Future<void> logout() async {
    await _realtime.disconnect();
    await _repository.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearError() {
    if (state.status == AuthStatus.failure || state.message != null) {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>(
  (ref) => AuthController(
    ref.watch(authRepositoryProvider),
    ref.watch(realtimeServiceProvider),
  ),
);
