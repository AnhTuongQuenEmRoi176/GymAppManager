import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/page_state.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';

class NotificationsPage extends ConsumerWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncItems = ref.watch(notificationsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Thông báo')),
      body: SafeArea(
        child: asyncItems.when(
          loading: () => const LoadingState(),
          error: (error, _) => ErrorState(
            message: error.toString(),
            onRetry: () => ref.invalidate(notificationsProvider),
          ),
          data: (items) {
            final sorted = [...items]
              ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
            return RefreshIndicator(
              onRefresh: () async => ref.invalidate(notificationsProvider),
              child: sorted.isEmpty
                  ? ListView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      children: const [
                        SizedBox(height: 130),
                        EmptyState(
                          title: 'Chưa có thông báo',
                          message: 'Các cập nhật về check-in, lịch tập và gói tập sẽ hiển thị tại đây.',
                          icon: Icons.notifications_none_rounded,
                        ),
                      ],
                    )
                  : ListView.separated(
                      padding: AppLayout.pageInsets,
                      itemCount: sorted.length,
                      separatorBuilder: (_, __) =>
                          const SizedBox(height: AppLayout.cardGap),
                      itemBuilder: (context, index) =>
                          _NotificationCard(item: sorted[index]),
                    ),
            );
          },
        ),
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({required this.item});

  final AppNotificationItem item;

  @override
  Widget build(BuildContext context) {
    final config = switch (item.type) {
      'checkin' => (
          Icons.qr_code_scanner_rounded,
          AppColors.success,
          AppColors.successSoft,
        ),
      'schedule' => (
          Icons.calendar_month_rounded,
          AppColors.primary,
          AppColors.primarySoft,
        ),
      'membership' => (
          Icons.workspace_premium_rounded,
          AppColors.tertiary,
          AppColors.tertiarySoft,
        ),
      _ => (
          Icons.notifications_none_rounded,
          AppColors.info,
          AppColors.infoSoft,
        ),
    };

    return AppCard(
      borderColor: item.isRead ? AppColors.border : AppColors.primaryBorder,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: config.$3,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(config.$1, color: config.$2, size: 21),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        item.title,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    if (!item.isRead) ...[
                      const SizedBox(width: 8),
                      Container(
                        width: 8,
                        height: 8,
                        margin: const EdgeInsets.only(top: 5),
                        decoration: const BoxDecoration(
                          color: AppColors.primary,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 5),
                Text(item.body, style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 8),
                Text(
                  AppFormatters.dateTime.format(item.createdAt),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontSize: 11,
                        color: AppColors.textMuted,
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
