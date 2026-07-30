enum UserRole {
  member,
  trainer;

  String get apiValue => switch (this) {
        UserRole.member => 'MEMBER',
        UserRole.trainer => 'TRAINER',
      };

  String get label => switch (this) {
        UserRole.member => 'Hội viên',
        UserRole.trainer => 'Huấn luyện viên',
      };

  static UserRole fromValue(String? value) {
    final normalized = value?.trim().toUpperCase();
    if (normalized == 'TRAINER' || normalized == 'PT') {
      return UserRole.trainer;
    }
    return UserRole.member;
  }
}

class AppUser {
  const AppUser({
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
  final UserRole role;
  final String? phone;
  final String? email;
  final String? avatarUrl;
}
