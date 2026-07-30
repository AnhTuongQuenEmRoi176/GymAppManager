import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/app_config.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../../auth/presentation/pages/change_password_page.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import 'notifications_page.dart';
import 'personal_information_page.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key, required this.user});

  final AppUser user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SafeArea(
      child: ListView(
        padding: AppLayout.pageInsets,
        children: [
          AppHeader(
            name: user.fullName,
            subtitle: 'Hồ sơ cá nhân',
            avatarUrl: user.avatarUrl,
            onNotifications: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => const NotificationsPage(),
              ),
            ),
          ),
          const SizedBox(height: 18),
          AppCard(
            child: Column(
              children: [
                AppAvatar(
                  name: user.fullName,
                  imageUrl: user.avatarUrl,
                  size: 88,
                  borderColor: AppColors.primaryBorder,
                ),
                const SizedBox(height: 13),
                Text(user.fullName, style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 4),
                Text(
                  user.role == UserRole.member
                      ? 'Mã HV: CS-${user.id.toString().padLeft(5, '0')}'
                      : 'Mã PT: PT-${user.id.toString().padLeft(5, '0')}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 13),
                Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    StatusChip(
                      label: user.role.label,
                      type: StatusType.info,
                      icon: Icons.badge_outlined,
                    ),
                    const StatusChip(
                      label: 'Đang hoạt động',
                      type: StatusType.success,
                      icon: Icons.check_rounded,
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: AppLayout.sectionGap),
          const _MenuTitle('TÀI KHOẢN'),
          const SizedBox(height: 8),
          AppCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _MenuItem(
                  icon: Icons.person_outline_rounded,
                  title: 'Thông tin cá nhân',
                  subtitle: 'Tên, số điện thoại, email và vai trò',
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => PersonalInformationPage(user: user),
                    ),
                  ),
                ),
                const Divider(),
                _MenuItem(
                  icon: Icons.lock_reset_rounded,
                  title: 'Đổi mật khẩu',
                  subtitle: 'Xác nhận mật khẩu hiện tại và nhập lại mật khẩu mới',
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => const ChangePasswordPage(),
                    ),
                  ),
                ),
                const Divider(),
                _MenuItem(
                  icon: Icons.notifications_none_rounded,
                  title: 'Thông báo',
                  subtitle: 'Check-in, lịch tập và trạng thái gói',
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => const NotificationsPage(),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppLayout.sectionGap),
          const _MenuTitle('PHIÊN ĐĂNG NHẬP'),
          const SizedBox(height: 8),
          AppCard(
            padding: EdgeInsets.zero,
            child: _MenuItem(
              icon: Icons.logout_rounded,
              iconColor: AppColors.error,
              iconBackground: AppColors.errorSoft,
              title: 'Đăng xuất',
              subtitle: 'Thoát tài khoản khỏi thiết bị này',
              titleColor: AppColors.error,
              onTap: () => _confirmLogout(context, ref),
            ),
          ),
          const SizedBox(height: 20),
          Center(
            child: Text(
              'CORE STRENGTH · Phiên bản 1.0.0${AppConfig.useMockData ? ' Demo' : ''}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontSize: 11,
                    color: AppColors.textMuted,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmLogout(BuildContext context, WidgetRef ref) async {
    final accepted = await showModalBottomSheet<bool>(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.errorSoft,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(Icons.logout_rounded, color: AppColors.error),
              ),
              const SizedBox(height: 14),
              Text('Đăng xuất?', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 6),
              Text(
                'Bạn sẽ cần đăng nhập lại để tiếp tục sử dụng ứng dụng.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 18),
              FilledButton(
                style: FilledButton.styleFrom(backgroundColor: AppColors.error),
                onPressed: () => Navigator.of(context).pop(true),
                child: const Text('Đăng xuất'),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text('Hủy'),
              ),
            ],
          ),
        ),
      ),
    );

    if (accepted == true) {
      await ref.read(authControllerProvider.notifier).logout();
    }
  }
}

class _MenuTitle extends StatelessWidget {
  const _MenuTitle(this.title);

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: const TextStyle(
        color: AppColors.textSecondary,
        fontSize: 11,
        fontWeight: FontWeight.w800,
        letterSpacing: 0.7,
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  const _MenuItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.iconColor = AppColors.primary,
    this.iconBackground = AppColors.primarySoft,
    this.titleColor = AppColors.textPrimary,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final Color iconColor;
  final Color iconBackground;
  final Color titleColor;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: iconBackground,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, size: 20, color: iconColor),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        color: titleColor,
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      subtitle,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right_rounded, color: AppColors.textMuted),
            ],
          ),
        ),
      ),
    );
  }
}
