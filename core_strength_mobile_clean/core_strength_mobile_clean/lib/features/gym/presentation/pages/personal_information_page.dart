import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../auth/domain/entities/app_user.dart';

class PersonalInformationPage extends StatelessWidget {
  const PersonalInformationPage({super.key, required this.user});

  final AppUser user;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Thông tin cá nhân')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
          children: [
            Center(
              child: AppAvatar(
                name: user.fullName,
                imageUrl: user.avatarUrl,
                size: 86,
                borderColor: AppColors.primaryBorder,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              user.fullName,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 4),
            Text(
              user.role.label,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 22),
            AppCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _InfoItem(
                    icon: Icons.badge_outlined,
                    label: 'Mã tài khoản',
                    value: user.role == UserRole.member
                        ? 'CS-${user.id.toString().padLeft(5, '0')}'
                        : 'PT-${user.id.toString().padLeft(5, '0')}',
                  ),
                  const Divider(),
                  _InfoItem(
                    icon: Icons.person_outline_rounded,
                    label: 'Tên đăng nhập',
                    value: user.username,
                  ),
                  const Divider(),
                  _InfoItem(
                    icon: Icons.phone_outlined,
                    label: 'Số điện thoại',
                    value: user.phone?.trim().isNotEmpty == true
                        ? user.phone!
                        : 'Chưa cập nhật',
                  ),
                  const Divider(),
                  _InfoItem(
                    icon: Icons.email_outlined,
                    label: 'Email',
                    value: user.email?.trim().isNotEmpty == true
                        ? user.email!
                        : 'Chưa cập nhật',
                  ),
                  const Divider(),
                  _InfoItem(
                    icon: Icons.verified_user_outlined,
                    label: 'Vai trò',
                    value: user.role.label,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            AppCard(
              color: AppColors.primarySoft,
              borderColor: AppColors.primaryBorder,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.info_outline_rounded, color: AppColors.primary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Thông tin cá nhân được đồng bộ từ hệ thống quản lý. Liên hệ lễ tân nếu cần thay đổi dữ liệu định danh.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppColors.primaryDark,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoItem extends StatelessWidget {
  const _InfoItem({required this.icon, required this.label, required this.value});

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: AppColors.primarySoft,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: AppColors.primary, size: 19),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 3),
                Text(
                  value,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
