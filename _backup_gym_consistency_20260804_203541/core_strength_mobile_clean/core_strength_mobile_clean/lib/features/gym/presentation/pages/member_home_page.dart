import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/page_state.dart';
import '../../../../core/widgets/section_header.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import '../widgets/quick_action_tile.dart';
import '../widgets/training_session_card.dart';
import 'notifications_page.dart';

// GYM_FLUTTER_HOME_MEMBERSHIP_FIX_V1
String _membershipSessionText(int? value) {
  return value == null ? 'Không giới hạn' : '$value buổi';
}

class MemberHomePage extends ConsumerWidget {
  const MemberHomePage({
    super.key,
    required this.user,
    required this.onNavigate,
  });

  final AppUser user;
  final ValueChanged<int> onNavigate;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(memberDashboardProvider);
    return SafeArea(
      child: asyncData.when(
        loading: () => const LoadingState(),
        error: (error, _) => ErrorState(
          message: error.toString(),
          onRetry: () => ref.invalidate(memberDashboardProvider),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(memberDashboardProvider),
          child: ListView(
            padding: AppLayout.pageInsets,
            children: [
              AppHeader(
                name: user.fullName,
                subtitle: 'Hội viên CORE STRENGTH',
                avatarUrl: user.avatarUrl,
                onNotifications: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => const NotificationsPage(),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              _MembershipCard(
                membership: data.membership,
                onTap: () => _showMembership(context, data.membership),
              ),
              const SizedBox(height: AppLayout.sectionGap),
              const SectionHeader(
                title: 'Truy cập nhanh',
                subtitle: 'Các chức năng bạn thường sử dụng',
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: QuickActionTile(
                      icon: Icons.qr_code_scanner_rounded,
                      label: 'QR Check-in',
                      subtitle: 'Mở mã cá nhân',
                      onTap: () => onNavigate(2),
                    ),
                  ),
                  const SizedBox(width: AppLayout.cardGap),
                  Expanded(
                    child: QuickActionTile(
                      icon: Icons.calendar_month_rounded,
                      label: 'Lịch tập',
                      subtitle: 'Xem lịch sắp tới',
                      onTap: () => onNavigate(1),
                      color: AppColors.info,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppLayout.cardGap),
              Row(
                children: [
                  Expanded(
                    child: QuickActionTile(
                      icon: Icons.workspace_premium_outlined,
                      label: 'Gói tập',
                      subtitle: 'Thông tin hội viên',
                      onTap: () => _showMembership(context, data.membership),
                      color: AppColors.secondary,
                    ),
                  ),
                  const SizedBox(width: AppLayout.cardGap),
                  Expanded(
                    child: QuickActionTile(
                      icon: Icons.history_rounded,
                      label: 'Lịch sử',
                      subtitle: 'Các lần check-in',
                      onTap: () => onNavigate(3),
                      color: AppColors.tertiary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppLayout.sectionGap),
              SectionHeader(
                title: 'Lịch tập gần nhất',
                actionLabel: 'Xem tất cả',
                onAction: () => onNavigate(1),
              ),
              const SizedBox(height: 10),
              if (data.upcomingSessions.isEmpty)
                const AppCard(
                  child: _InlineEmpty(
                    icon: Icons.event_available_outlined,
                    text: 'Chưa có lịch tập sắp tới.',
                  ),
                )
              else
                TrainingSessionCard(
                  session: data.upcomingSessions.first,
                  compact: true,
                  onTap: () => onNavigate(1),
                ),
              const SizedBox(height: AppLayout.sectionGap),
              const SectionHeader(title: 'Hoạt động gần đây'),
              const SizedBox(height: 10),
              AppCard(
                padding: EdgeInsets.zero,
                child: data.recentActivities.isEmpty
                    ? const Padding(
                        padding: EdgeInsets.all(16),
                        child: _InlineEmpty(
                          icon: Icons.notifications_none_rounded,
                          text: 'Chưa có hoạt động gần đây.',
                        ),
                      )
                    : Column(
                        children: [
                          for (var index = 0;
                              index < data.recentActivities.length;
                              index++) ...[
                            _ActivityRow(item: data.recentActivities[index]),
                            if (index != data.recentActivities.length - 1)
                              const Divider(),
                          ],
                        ],
                      ),
              ),
              const SizedBox(height: AppLayout.cardGap),
              AppCard(
                color: AppColors.primarySoft,
                borderColor: AppColors.primaryBorder,
                child: Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: const Icon(
                        Icons.insights_rounded,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Thống kê tháng này',
                            style: TextStyle(
                              color: AppColors.primaryDark,
                              fontSize: 13,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            'Bạn đã check-in ${data.monthlyCheckins} lần tại phòng gym.',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: AppColors.primaryDark,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showMembership(BuildContext context, MembershipSummary membership) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Thông tin gói tập', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 16),
              _DetailRow(label: 'Tên gói', value: membership.packageName),
              _DetailRow(
                label: 'Ngày bắt đầu',
                value: AppFormatters.date.format(membership.startDate),
              ),
              _DetailRow(
                label: 'Ngày hết hạn',
                value: AppFormatters.date.format(membership.endDate),
              ),
              _DetailRow(
                label: 'PT phụ trách',
                value: membership.trainerName ?? 'Không đăng ký PT',
              ),
              _DetailRow(
                label: membership.sessionLabel,
                value: _membershipSessionText(membership.sessionsRemaining),
              ),
              if (membership.ptPackageName != null &&
                  membership.ptPackageName != membership.packageName) ...[
                _DetailRow(label: 'Gói PT', value: membership.ptPackageName!),
                _DetailRow(
                  label: 'Buổi PT còn lại',
                  value: _membershipSessionText(membership.ptSessionsRemaining),
                ),
              ],
              const SizedBox(height: 18),
              FilledButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Đóng'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MembershipCard extends StatelessWidget {
  const _MembershipCard({required this.membership, required this.onTap});

  final MembershipSummary membership;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppLayout.cardRadius),
        child: Ink(
          padding: const EdgeInsets.all(17),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.primary, AppColors.primaryDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(AppLayout.cardRadius),
            boxShadow: const [
              BoxShadow(
                color: Color(0x2A2027A8),
                blurRadius: 20,
                offset: Offset(0, 8),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'GÓI TẬP HIỆN TẠI',
                          style: TextStyle(
                            color: Color(0xFFC9CCFF),
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          membership.packageName,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                  ),
                  StatusChip(
                    label: membership.status,
                    type: StatusType.success,
                    icon: Icons.check_rounded,
                  ),
                ],
              ),
              const SizedBox(height: 17),
              ClipRRect(
                borderRadius: BorderRadius.circular(99),
                child: LinearProgressIndicator(
                  value: membership.progress,
                  minHeight: 7,
                  backgroundColor: Colors.white.withOpacity(0.20),
                  color: const Color(0xFF7CE49A),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Text(
                    'Tiến độ sử dụng',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.74),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '${(membership.progress * 100).round()}%',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _MembershipMetric(
                      icon: Icons.calendar_today_outlined,
                      label: 'Hết hạn',
                      value: AppFormatters.date.format(membership.endDate),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _MembershipMetric(
                      icon: Icons.repeat_rounded,
                      label: membership.sessionLabel,
                value: _membershipSessionText(membership.sessionsRemaining),
                    ),
                  ),
                ],
              ),
              if (membership.ptPackageName != null &&
                  membership.ptPackageName != membership.packageName) ...[
                const SizedBox(height: 10),
                _MembershipMetric(
                  icon: Icons.fitness_center_rounded,
                  label: 'Buổi PT còn lại',
                  value: _membershipSessionText(membership.ptSessionsRemaining),
                ),
              ],
              const SizedBox(height: 10),
              _MembershipMetric(
                icon: Icons.person_outline_rounded,
                label: 'PT phụ trách',
                value: membership.trainerName ?? 'Không đăng ký PT',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MembershipMetric extends StatelessWidget {
  const _MembershipMetric({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.10),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.12)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 17, color: Colors.white),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.68),
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ActivityRow extends StatelessWidget {
  const _ActivityRow({required this.item});

  final ActivityItem item;

  @override
  Widget build(BuildContext context) {
    final config = switch (item.type) {
      'checkin' => (Icons.check_circle_outline_rounded, AppColors.success),
      'session' => (Icons.fitness_center_rounded, AppColors.primary),
      'payment' => (Icons.account_balance_wallet_outlined, AppColors.tertiary),
      _ => (Icons.notifications_none_rounded, AppColors.info),
    };

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: config.$2.withOpacity(0.10),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(config.$1, color: config.$2, size: 19),
          ),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 3),
                Text(
                  item.subtitle,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            AppFormatters.time.format(item.occurredAt),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10),
          ),
        ],
      ),
    );
  }
}

class _InlineEmpty extends StatelessWidget {
  const _InlineEmpty({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: AppColors.textMuted),
        const SizedBox(width: 10),
        Expanded(child: Text(text, style: Theme.of(context).textTheme.bodySmall)),
      ],
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: Theme.of(context).textTheme.bodySmall),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}
