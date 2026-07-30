import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/metric_card.dart';
import '../../../../core/widgets/page_state.dart';
import '../../../../core/widgets/section_header.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import '../widgets/training_session_card.dart';
import 'notifications_page.dart';

class TrainerHomePage extends ConsumerWidget {
  const TrainerHomePage({
    super.key,
    required this.user,
    required this.onNavigate,
  });

  final AppUser user;
  final ValueChanged<int> onNavigate;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(trainerDashboardProvider);
    return SafeArea(
      child: asyncData.when(
        loading: () => const LoadingState(),
        error: (error, _) => ErrorState(
          message: error.toString(),
          onRetry: () => ref.invalidate(trainerDashboardProvider),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(trainerDashboardProvider),
          child: ListView(
            padding: AppLayout.pageInsets,
            children: [
              AppHeader(
                name: user.fullName,
                subtitle: 'Huấn luyện viên cá nhân',
                avatarUrl: user.avatarUrl,
                onNotifications: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => const NotificationsPage(),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              _WorkingStatusCard(isWorking: data.isWorking),
              const SizedBox(height: AppLayout.sectionGap),
              const SectionHeader(
                title: 'Thống kê tổng quan',
                subtitle: 'Dữ liệu được cập nhật từ hệ thống quản lý',
              ),
              const SizedBox(height: 10),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: AppLayout.cardGap,
                mainAxisSpacing: AppLayout.cardGap,
                childAspectRatio: 1.26,
                children: [
                  MetricCard(
                    icon: Icons.calendar_today_rounded,
                    value: '${data.stats.todaySessions}',
                    label: 'Lịch dạy hôm nay',
                  ),
                  MetricCard(
                    icon: Icons.groups_2_outlined,
                    value: '${data.stats.assignedMembers}',
                    label: 'Hội viên phụ trách',
                    accent: AppColors.secondary,
                    onTap: () => onNavigate(3),
                  ),
                  MetricCard(
                    icon: Icons.fitness_center_rounded,
                    value: '${data.stats.monthlySessions}',
                    label: 'Buổi dạy tháng này',
                    accent: AppColors.tertiary,
                  ),
                  MetricCard(
                    icon: Icons.account_balance_wallet_outlined,
                    value: AppFormatters.compactCurrency(
                      data.stats.estimatedIncome,
                    ),
                    label: 'Thu nhập tạm tính',
                    accent: AppColors.info,
                  ),
                ],
              ),
              const SizedBox(height: AppLayout.sectionGap),
              SectionHeader(
                title: 'Lịch dạy hôm nay',
                actionLabel: 'Xem tất cả',
                onAction: () => onNavigate(1),
              ),
              const SizedBox(height: 10),
              if (data.todaySessions.isEmpty)
                const AppCard(
                  child: Row(
                    children: [
                      Icon(
                        Icons.event_available_outlined,
                        color: AppColors.textMuted,
                      ),
                      SizedBox(width: 10),
                      Expanded(child: Text('Hôm nay chưa có lịch dạy.')),
                    ],
                  ),
                )
              else
                ...data.todaySessions.map(
                  (session) => Padding(
                    padding: const EdgeInsets.only(bottom: AppLayout.cardGap),
                    child: TrainingSessionCard(
                      session: session,
                      compact: true,
                      onTap: () => onNavigate(1),
                    ),
                  ),
                ),
              const SizedBox(height: 8),
              SectionHeader(
                title: 'Hội viên cần chú ý',
                actionLabel: 'Danh sách',
                onAction: () => onNavigate(3),
              ),
              const SizedBox(height: 10),
              if (data.alerts.isEmpty)
                const AppCard(
                  child: Row(
                    children: [
                      Icon(
                        Icons.check_circle_outline_rounded,
                        color: AppColors.success,
                      ),
                      SizedBox(width: 10),
                      Expanded(child: Text('Không có cảnh báo cần xử lý.')),
                    ],
                  ),
                )
              else
                ...data.alerts.map(
                  (alert) => Padding(
                    padding: const EdgeInsets.only(bottom: AppLayout.cardGap),
                    child: _AlertCard(
                      alert: alert,
                      onTap: () => onNavigate(3),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _WorkingStatusCard extends StatelessWidget {
  const _WorkingStatusCard({required this.isWorking});

  final bool isWorking;

  @override
  Widget build(BuildContext context) {
    final color = isWorking ? AppColors.success : AppColors.textSecondary;
    return AppCard(
      borderColor: isWorking ? AppColors.successBorder : AppColors.border,
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: isWorking ? AppColors.successSoft : AppColors.surfaceMuted,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(
              isWorking
                  ? Icons.check_circle_outline_rounded
                  : Icons.pause_circle_outline_rounded,
              color: color,
              size: 22,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Trạng thái làm việc',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 3),
                Text(
                  isWorking ? 'Đang sẵn sàng nhận lịch' : 'Đang tạm nghỉ',
                  style: TextStyle(
                    color: color,
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
          StatusChip(
            label: isWorking ? 'Đang làm việc' : 'Tạm nghỉ',
            type: isWorking ? StatusType.success : StatusType.neutral,
          ),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  const _AlertCard({required this.alert, required this.onTap});

  final MemberAlert alert;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isDanger = alert.severity == 'danger';
    final accent = isDanger ? AppColors.error : AppColors.warning;
    final soft = isDanger ? AppColors.errorSoft : AppColors.warningSoft;

    return AppCard(
      onTap: onTap,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: soft,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(
              isDanger
                  ? Icons.warning_amber_rounded
                  : Icons.info_outline_rounded,
              color: accent,
              size: 21,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.memberName,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(alert.message, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Icon(Icons.chevron_right_rounded, color: accent, size: 20),
        ],
      ),
    );
  }
}
