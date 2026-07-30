import 'dart:async';

import '../../../../core/network/api_exception.dart';
import '../../../../core/storage/token_storage.dart';
import '../../domain/entities/app_user.dart';
import '../../domain/entities/auth_session.dart';
import '../../domain/repositories/auth_repository.dart';

class MockAuthRepository implements AuthRepository {
  MockAuthRepository(this._storage);

  final TokenStorage _storage;

  @override
  Future<AuthSession?> restoreSession() async {
    await Future<void>.delayed(const Duration(milliseconds: 500));
    final token = await _storage.readAccessToken();
    final roleValue = await _storage.readRole();
    if (token == null || roleValue == null) return null;
    final role = UserRole.fromValue(roleValue);
    return _sessionForRole(role, token: token);
  }

  @override
  Future<AuthSession> login({
    required String username,
    required String password,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 650));
    if (password != '123456') {
      throw const ApiException('Tài khoản hoặc mật khẩu không đúng.');
    }
    final normalized = username.trim().toLowerCase();
    final role = normalized.contains('trainer') ||
            normalized.contains('pt') ||
            normalized == '0912345678'
        ? UserRole.trainer
        : UserRole.member;
    final session = _sessionForRole(role, token: 'demo-${role.apiValue}');
    await _storage.saveSession(
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
      role: role.apiValue,
    );
    return session;
  }

  AuthSession _sessionForRole(UserRole role, {required String token}) {
    if (role == UserRole.trainer) {
      return AuthSession(
        user: const AppUser(
          id: 2,
          fullName: 'PT Minh Quân',
          username: 'trainer',
          phone: '0912345678',
          email: 'pt.minhquan@corestrength.vn',
          role: UserRole.trainer,
        ),
        accessToken: token,
        refreshToken: 'demo-refresh-trainer',
      );
    }
    return AuthSession(
      user: const AppUser(
        id: 1,
        fullName: 'Nguyễn Văn A',
        username: 'member',
        phone: '0987654321',
        email: 'member@corestrength.vn',
        role: UserRole.member,
      ),
      accessToken: token,
      refreshToken: 'demo-refresh-member',
    );
  }

  @override
  Future<PasswordResetRequestResult> requestPasswordReset(String account) async {
    await Future<void>.delayed(const Duration(milliseconds: 500));
    return const PasswordResetRequestResult(
      message: 'Mã OTP demo đã được tạo.',
      debugOtp: '123456',
    );
  }

  @override
  Future<void> resetPassword({
    required String account,
    required String otp,
    required String newPassword,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 550));
    if (otp != '123456') {
      throw const ApiException('Mã OTP không đúng hoặc đã hết hạn.');
    }
  }

  @override
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 550));
    if (currentPassword != '123456') {
      throw const ApiException('Mật khẩu hiện tại không đúng.');
    }
  }

  @override
  Future<void> logout() => _storage.clear();
}
