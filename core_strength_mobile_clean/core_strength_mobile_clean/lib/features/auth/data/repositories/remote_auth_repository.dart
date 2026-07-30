import '../../../../core/storage/token_storage.dart';
import '../../domain/entities/auth_session.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_data_source.dart';

class RemoteAuthRepository implements AuthRepository {
  RemoteAuthRepository({
    required AuthRemoteDataSource remote,
    required TokenStorage storage,
  })  : _remote = remote,
        _storage = storage;

  final AuthRemoteDataSource _remote;
  final TokenStorage _storage;

  @override
  Future<AuthSession?> restoreSession() async {
    final token = await _storage.readAccessToken();
    if (token == null || token.isEmpty) return null;
    try {
      final user = (await _remote.getMe()).toEntity();
      return AuthSession(
        user: user,
        accessToken: token,
        refreshToken: await _storage.readRefreshToken(),
      );
    } catch (_) {
      await _storage.clear();
      return null;
    }
  }

  @override
  Future<AuthSession> login({
    required String username,
    required String password,
  }) async {
    final result = await _remote.login(username: username, password: password);
    final user = result.user.toEntity();
    await _storage.saveSession(
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
      role: user.role.apiValue,
    );
    return AuthSession(
      user: user,
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
    );
  }

  @override
  Future<PasswordResetRequestResult> requestPasswordReset(String account) {
    return _remote.requestPasswordReset(account);
  }

  @override
  Future<void> resetPassword({
    required String account,
    required String otp,
    required String newPassword,
  }) {
    return _remote.resetPassword(
      account: account,
      otp: otp,
      newPassword: newPassword,
    );
  }

  @override
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) {
    return _remote.changePassword(
      currentPassword: currentPassword,
      newPassword: newPassword,
    );
  }

  @override
  Future<void> logout() => _storage.clear();
}
