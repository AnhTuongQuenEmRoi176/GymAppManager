import '../entities/auth_session.dart';

abstract class AuthRepository {
  Future<AuthSession?> restoreSession();

  Future<AuthSession> login({
    required String username,
    required String password,
  });

  Future<PasswordResetRequestResult> requestPasswordReset(String account);

  Future<void> resetPassword({
    required String account,
    required String otp,
    required String newPassword,
  });

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  });

  Future<void> logout();
}
