import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/page_state.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import '../widgets/training_session_card.dart';
import 'notifications_page.dart';
import 'schedule_form_page.dart';

class SchedulePage extends ConsumerStatefulWidget {
  const SchedulePage({super.key, required this.user});

  final AppUser user;

  @override
  ConsumerState<SchedulePage> createState() => _SchedulePageState();
}

class _SchedulePageState extends ConsumerState<SchedulePage> {
  int _segment = 0;

  bool get _isTrainer => widget.user.role == UserRole.trainer;

  @override
  Widget build(BuildContext context) {
    final asyncSessions = ref.watch(scheduleProvider(widget.user.role));
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
              subtitle: _isTrainer ? 'Lịch dạy PT' : 'Lịch tập cá nhân',
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
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _isTrainer ? 'Lịch dạy' : 'Lịch tập',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 5),
                          Text(
                            _isTrainer
                                ? 'Tạo và quản lý lịch với hội viên của bạn.'
                                : 'Theo dõi thời gian và trạng thái từng buổi tập.',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    if (_isTrainer) ...[
                      const SizedBox(width: 12),
                      FilledButton.icon(
                        onPressed: _openCreateSchedule,
                        style: FilledButton.styleFrom(
                          minimumSize: const Size(0, 44),
                          padding: const EdgeInsets.symmetric(horizontal: 14),
                        ),
                        icon: const Icon(Icons.add_rounded, size: 19),
                        label: const Text('Tạo lịch'),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  child: SegmentedButton<int>(
                    segments: const [
                      ButtonSegment(value: 0, label: Text('Hôm nay')),
                      ButtonSegment(value: 1, label: Text('Tuần này')),
                      ButtonSegment(value: 2, label: Text('Tháng này')),
                    ],
                    selected: {_segment},
                    showSelectedIcon: false,
                    onSelectionChanged: (values) {
                      setState(() => _segment = values.first);
                    },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: asyncSessions.when(
              loading: () => const LoadingState(),
              error: (error, _) => ErrorState(
                message: error.toString(),
                onRetry: () => ref.invalidate(scheduleProvider(widget.user.role)),
              ),
              data: (sessions) {
                final filtered = _filterSessions(sessions)
                  ..sort((a, b) => a.startAt.compareTo(b.startAt));

                if (filtered.isEmpty) {
                  return RefreshIndicator(
                    onRefresh: _refresh,
                    child: ListView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppLayout.pagePadding,
                      ),
                      children: [
                        const SizedBox(height: 100),
                        EmptyState(
                          title: 'Chưa có lịch',
                          message: _isTrainer
                              ? 'Bạn chưa có buổi dạy trong khoảng thời gian này.'
                              : 'Không có buổi tập trong khoảng thời gian này.',
                          icon: Icons.calendar_month_outlined,
                        ),
                        if (_isTrainer) ...[
                          const SizedBox(height: 18),
                          FilledButton.icon(
                            onPressed: _openCreateSchedule,
                            icon: const Icon(Icons.add_rounded),
                            label: const Text('Tạo lịch dạy đầu tiên'),
                          ),
                        ],
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: _refresh,
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(
                      AppLayout.pagePadding,
                      0,
                      AppLayout.pagePadding,
                      AppLayout.pageBottomPadding,
                    ),
                    itemCount: filtered.length + 1,
                    separatorBuilder: (_, __) =>
                        const SizedBox(height: AppLayout.cardGap),
                    itemBuilder: (context, index) {
                      if (index == 0) {
                        return Row(
                          children: [
                            Expanded(
                              child: Text(
                                _periodTitle,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: AppColors.primarySoft,
                                borderRadius: BorderRadius.circular(99),
                                border: Border.all(color: AppColors.primaryBorder),
                              ),
                              child: Text(
                                '${filtered.length} lịch',
                                style: const TextStyle(
                                  color: AppColors.primary,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                          ],
                        );
                      }

                      final session = filtered[index - 1];
                      return TrainingSessionCard(
                        session: session,
                        onTap: () => _showSessionDetail(context, session),
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

  String get _periodTitle => switch (_segment) {
        0 => 'Lịch hôm nay',
        1 => 'Lịch trong tuần',
        _ => 'Lịch trong tháng',
      };

  List<TrainingSession> _filterSessions(List<TrainingSession> sessions) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final weekStart = today.subtract(Duration(days: today.weekday - 1));
    final weekEnd = weekStart.add(const Duration(days: 7));

    return sessions.where((session) {
      final date = session.startAt;
      final day = DateTime(date.year, date.month, date.day);
      if (_segment == 0) return day == today;
      if (_segment == 1) {
        return !day.isBefore(weekStart) && day.isBefore(weekEnd);
      }
      return date.year == now.year && date.month == now.month;
    }).toList();
  }

  Future<void> _refresh() async {
    ref.invalidate(scheduleProvider(widget.user.role));
    if (_isTrainer) {
      ref.invalidate(trainerDashboardProvider);
      ref.invalidate(assignedMembersProvider);
    } else {
      ref.invalidate(memberDashboardProvider);
    }
  }

  Future<void> _openCreateSchedule() async {
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute<bool>(builder: (_) => const ScheduleFormPage()),
    );
    if (changed == true && mounted) {
      await _refresh();
      _showMessage('Đã tạo lịch dạy.');
    }
  }

  Future<void> _openEditSchedule(TrainingSession session) async {
    Navigator.of(context).pop();
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute<bool>(
        builder: (_) => ScheduleFormPage(existing: session),
      ),
    );
    if (changed == true && mounted) {
      await _refresh();
      _showMessage('Đã cập nhật lịch dạy.');
    }
  }

  Future<void> _cancelSchedule(TrainingSession session) async {
    Navigator.of(context).pop();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hủy lịch dạy?'),
        content: Text(
          'Lịch “${session.title}” với ${session.participantName} sẽ được chuyển sang trạng thái đã hủy.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Không'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.error,
              minimumSize: const Size(0, 42),
            ),
            child: const Text('Hủy lịch'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      await ref.read(gymRepositoryProvider).cancelSchedule(session.id);
      if (!mounted) return;
      await _refresh();
      _showMessage('Đã hủy lịch dạy.');
    } catch (error) {
      if (!mounted) return;
      _showMessage(error.toString());
    }
  }

  void _showSessionDetail(BuildContext context, TrainingSession session) {
    final canChange = _isTrainer && session.status.canBeChanged;
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
              Text(session.title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 16),
              _SheetInfo(
                icon: Icons.person_outline_rounded,
                label: _isTrainer ? 'Hội viên' : 'Huấn luyện viên',
                value: session.participantName,
              ),
              _SheetInfo(
                icon: Icons.calendar_today_outlined,
                label: 'Ngày',
                value: AppFormatters.date.format(session.startAt),
              ),
              _SheetInfo(
                icon: Icons.schedule_rounded,
                label: 'Thời gian',
                value:
                    '${AppFormatters.time.format(session.startAt)} - ${AppFormatters.time.format(session.endAt)}',
              ),
              if (session.location != null && session.location!.trim().isNotEmpty)
                _SheetInfo(
                  icon: Icons.place_outlined,
                  label: 'Địa điểm',
                  value: session.location!,
                ),
              _SheetInfo(
                icon: Icons.info_outline_rounded,
                label: 'Trạng thái',
                value: session.status.label,
              ),
              if (session.note != null && session.note!.trim().isNotEmpty)
                _SheetInfo(
                  icon: Icons.notes_rounded,
                  label: 'Ghi chú',
                  value: session.note!,
                ),
              const SizedBox(height: 18),
              if (canChange) ...[
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _openEditSchedule(session),
                        icon: const Icon(Icons.edit_outlined),
                        label: const Text('Sửa lịch'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _cancelSchedule(session),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppColors.error,
                          side: const BorderSide(color: AppColors.errorBorder),
                        ),
                        icon: const Icon(Icons.event_busy_outlined),
                        label: const Text('Hủy lịch'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
              ],
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

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }
}

class _SheetInfo extends StatelessWidget {
  const _SheetInfo({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
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
