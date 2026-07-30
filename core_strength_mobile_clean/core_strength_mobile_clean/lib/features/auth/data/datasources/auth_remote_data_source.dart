import '../../../../core/network/api_client.dart';
import '../../domain/entities/auth_session.dart';
import '../models/user_model.dart';

class AuthRemoteDataSource {
  const AuthRemoteDataSource(this._client);

  final ApiClient _client;

  Future<RemoteAuthResult> login({
    required String username,
    required String password,
  }) async {
    final json = await _client.postJson(
      '/auth/login',
      data: {'username': username, 'password': password},
    );
    return RemoteAuthResult.fromJson(json);
  }

  Future<UserModel> getMe() async {
    final json = await _client.getJson('/auth/me');
    return UserModel.fromJson(
      json['user'] is Map<String, dynamic>
          ? json['user'] as Map<String, dynamic>
          : json,
    );
  }

  Future<PasswordResetRequestResult> requestPasswordReset(String account) async {
    final json = await _client.postJson(
      '/auth/forgot-password',
      data: {'account': account},
    );
    return PasswordResetRequestResult(
      message: json['message']?.toString() ?? 'Mã xác thực đã được tạo.',
      debugOtp: json['debug_otp']?.toString(),
    );
  }

  Future<void> resetPassword({
    required String account,
    required String otp,
    required String newPassword,
  }) async {
    await _client.postJson(
      '/auth/reset-password',
      data: {
        'account': account,
        'otp': otp,
        'new_password': newPassword,
      },
    );
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _client.postJson(
      '/auth/change-password',
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      },
    );
  }
}

class RemoteAuthResult {
  const RemoteAuthResult({
    required this.accessToken,
    required this.user,
    this.refreshToken,
  });

  final String accessToken;
  final String? refreshToken;
  final UserModel user;

  factory RemoteAuthResult.fromJson(Map<String, dynamic> json) {
    final userJson = json['user'];
    if (userJson is! Map) {
      throw const FormatException('Phản hồi đăng nhập thiếu thông tin user.');
    }
    return RemoteAuthResult(
      accessToken: json['access_token']?.toString() ?? '',
      refreshToken: json['refresh_token']?.toString(),
      user: UserModel.fromJson(userJson.cast<String, dynamic>()),
    );
  }
}
