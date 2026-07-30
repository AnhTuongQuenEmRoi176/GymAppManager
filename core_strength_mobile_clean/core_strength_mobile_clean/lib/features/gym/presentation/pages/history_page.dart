import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/page_state.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import 'notifications_page.dart';

class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key, required this.user});

  final AppUser user;

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage> {
  DateTime? _selectedDate;

  @override
  Widget build(BuildContext context) {
    final asyncRecords = ref.watch(checkinHistoryProvider);
    return SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppLayout.pagePadding,
              AppLayout.pageTopPadding,
              AppLayout.pagePadding,
              0,
            ),
            child: AppHeader(
              name: widget.user.fullName,
              subtitle: 'Lịch sử hoạt động',
              avatarUrl: widget.user.avatarUrl,
              onNotifications: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const NotificationsPage(),
                ),
              ),
            ),
          ),
          const SizedBox(height: 18),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppLayout.pagePadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Lịch sử Check-in', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 5),
                Text(
                  'Xem lại thời gian và nguồn xác nhận check-in.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _pickDate,
                        icon: const Icon(Icons.calendar_month_outlined),
                        label: Text(
                          _selectedDate == null
                              ? 'Lọc theo ngày'
                              : AppFormatters.date.format(_selectedDate!),
                        ),
                      ),
                    ),
                    if (_selectedDate != null) ...[
                      const SizedBox(width: 10),
                      IconButton.outlined(
                        onPressed: () => setState(() => _selectedDate = null),
                        tooltip: 'Xóa bộ lọc',
                        icon: const Icon(Icons.close_rounded),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: asyncRecords.when(
              loading: () => const LoadingState(),
              error: (error, _) => ErrorState(
                message: error.toString(),
                onRetry: () => ref.invalidate(checkinHistoryProvider),
              ),
              data: (records) {
                final filtered = records.where(_matchesDate).toList()
                  ..sort((a, b) => b.scannedAt.compareTo(a.scannedAt));

                return RefreshIndicator(
                  onRefresh: () async => ref.invalidate(checkinHistoryProvider),
                  child: filtered.isEmpty
                      ? ListView(
                          physics: const AlwaysScrollableScrollPhysics(),
                          children: [
                            const SizedBox(height: 110),
                            EmptyState(
                              title: _selectedDate == null
                                  ? 'Chưa có lịch sử'
                                  : 'Không có dữ liệu trong ngày này',
                              message: _selectedDate == null
                                  ? 'Các lần check-in sẽ hiển thị tại đây.'
                                  : 'Hãy chọn ngày khác hoặc xóa bộ lọc.',
                              icon: Icons.history_toggle_off_rounded,
                            ),
                          ],
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.fromLTRB(
                            AppLayout.pagePadding,
                            0,
                            AppLayout.pagePadding,
                            AppLayout.pageBottomPadding,
                          ),
                          itemCount: filtered.length,
                          separatorBuilder: (_, __) =>
                              const SizedBox(height: AppLayout.cardGap),
                          itemBuilder: (context, index) {
                            final record = filtered[index];
                            return _HistoryCard(
                              record: record,
                              onTap: () => _showDetail(context, record),
                            );
                          },
                        ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  bool _matchesDate(CheckinRecord record) {
    if (_selectedDate == null) return true;
    final a = record.scannedAt;
    final b = _selectedDate!;
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  Future<void> _pickDate() async {
    final selected = await showDatePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      initialDate: _selectedDate ?? DateTime.now(),
    );
    if (selected != null && mounted) {
      setState(() => _selectedDate = selected);
    }
  }

  void _showDetail(BuildContext context, CheckinRecord record) {
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
              Text('Chi tiết Check-in', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 16),
              _DetailLine(
                icon: Icons.schedule_rounded,
                label: 'Thời gian',
                value: AppFormatters.dateTime.format(record.scannedAt),
              ),
              _DetailLine(
                icon: Icons.place_outlined,
                label: 'Vị trí',
                value: record.location,
              ),
              _DetailLine(
                icon: Icons.qr_code_scanner_rounded,
                label: 'Nguồn',
                value: record.source,
              ),
              _DetailLine(
                icon: Icons.check_circle_outline_rounded,
                label: 'Trạng thái',
                value: record.status,
              ),
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

class _HistoryCard extends StatelessWidget {
  const _HistoryCard({required this.record, required this.onTap});

  final CheckinRecord record;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: onTap,
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppColors.successSoft,
              borderRadius: BorderRadius.circular(13),
            ),
            child: const Icon(
              Icons.login_rounded,
              color: AppColors.success,
              size: 21,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Check-in thành công',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(
                  record.location,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                Text(
                  AppFormatters.dateTime.format(record.scannedAt),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 11),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          const StatusChip(label: 'Thành công', type: StatusType.success),
        ],
      ),
    );
  }
}

class _DetailLine extends StatelessWidget {
  const _DetailLine({required this.icon, required this.label, required this.value});

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.primarySoft,
              borderRadius: BorderRadius.circular(11),
            ),
            child: Icon(icon, color: AppColors.primary, size: 18),
          ),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
