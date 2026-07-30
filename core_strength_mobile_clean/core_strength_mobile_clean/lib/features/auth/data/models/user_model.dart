import '../../../../core/config/app_config.dart';
import '../../domain/entities/app_user.dart';

class UserModel {
  const UserModel({
    required this.id,
    required this.fullName,
    required this.username,
    required this.role,
    this.phone,
    this.email,
    this.avatarUrl,
  });

  final int id;
  final String fullName;
  final String username;
  final String role;
  final String? phone;
  final String? email;
  final String? avatarUrl;

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: int.tryParse(json['id']?.toString() ?? '') ?? 0,
      fullName: json['full_name']?.toString() ??
          json['fullName']?.toString() ??
          'Người dùng',
      username: json['username']?.toString() ?? '',
      role: json['role'] is Map
          ? (json['role'] as Map)['name']?.toString() ?? 'MEMBER'
          : json['role']?.toString() ?? 'MEMBER',
      phone: json['phone']?.toString(),
      email: json['email']?.toString(),
      avatarUrl: AppConfig.resolvePublicUrl(
        json['avatar']?.toString() ?? json['avatar_url']?.toString(),
      ),
    );
  }

  AppUser toEntity() {
    return AppUser(
      id: id,
      fullName: fullName,
      username: username,
      role: UserRole.fromValue(role),
      phone: phone,
      email: email,
      avatarUrl: avatarUrl,
    );
  }
}
