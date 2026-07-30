import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/page_state.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import 'notifications_page.dart';

class TrainerMembersPage extends ConsumerStatefulWidget {
  const TrainerMembersPage({super.key, required this.user});

  final AppUser user;

  @override
  ConsumerState<TrainerMembersPage> createState() => _TrainerMembersPageState();
}

class _TrainerMembersPageState extends ConsumerState<TrainerMembersPage> {
  final _searchController = TextEditingController();
  String _keyword = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final asyncMembers = ref.watch(assignedMembersProvider);
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
              subtitle: 'Hội viên đang phụ trách',
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
                Text('Danh sách hội viên', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 5),
                Text(
                  'Tìm kiếm và theo dõi gói tập của từng hội viên.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: _searchController,
                  onChanged: (value) {
                    setState(() => _keyword = value.trim().toLowerCase());
                  },
                  decoration: InputDecoration(
                    hintText: 'Tìm theo tên hoặc số điện thoại',
                    prefixIcon: const Icon(Icons.search_rounded),
                    suffixIcon: _keyword.isEmpty
                        ? null
                        : IconButton(
                            onPressed: () {
                              _searchController.clear();
                              setState(() => _keyword = '');
                            },
                            icon: const Icon(Icons.close_rounded),
                          ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: asyncMembers.when(
              loading: () => const LoadingState(),
              error: (error, _) => ErrorState(
                message: error.toString(),
                onRetry: () => ref.invalidate(assignedMembersProvider),
              ),
              data: (members) {
                final filtered = members.where((member) {
                  if (_keyword.isEmpty) return true;
                  return member.fullName.toLowerCase().contains(_keyword) ||
                      member.phone.toLowerCase().contains(_keyword);
                }).toList()
                  ..sort((a, b) => a.fullName.compareTo(b.fullName));

                return RefreshIndicator(
                  onRefresh: () async => ref.invalidate(assignedMembersProvider),
                  child: filtered.isEmpty
                      ? ListView(
                          physics: const AlwaysScrollableScrollPhysics(),
                          children: const [
                            SizedBox(height: 110),
                            EmptyState(
                              title: 'Không tìm thấy hội viên',
                              message: 'Thử tìm bằng tên hoặc số điện thoại khác.',
                              icon: Icons.group_off_outlined,
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
                            final member = filtered[index];
                            return _MemberCard(
                              member: member,
                              onTap: () => _showDetail(context, member),
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

  void _showDetail(BuildContext context, AssignedMember member) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AppAvatar(name: member.fullName, size: 72),
              const SizedBox(height: 12),
              Text(member.fullName, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(member.phone, style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 18),
              AppCard(
                color: AppColors.surfaceMuted,
                child: Column(
                  children: [
                    _DetailRow(label: 'Gói hiện tại', value: member.packageName),
                    const Divider(),
                    _DetailRow(
                      label: 'Buổi PT còn lại',
                      value: '${member.sessionsRemaining} buổi',
                    ),
                    const Divider(),
                    _DetailRow(
                      label: 'Ngày hết hạn',
                      value: AppFormatters.date.format(member.endDate),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              FilledButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.calendar_month_rounded),
                label: const Text('Đóng'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MemberCard extends StatelessWidget {
  const _MemberCard({required this.member, required this.onTap});

  final AssignedMember member;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final lowSessions = member.sessionsRemaining <= 3;
    final expiringSoon = member.endDate.difference(DateTime.now()).inDays <= 7;

    return AppCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              AppAvatar(name: member.fullName, size: 46),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      member.fullName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 3),
                    Text(member.phone, style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
              StatusChip(
                label: '${member.sessionsRemaining} buổi',
                type: lowSessions ? StatusType.warning : StatusType.success,
              ),
            ],
          ),
          const SizedBox(height: 13),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.surfaceMuted,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.divider),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  member.packageName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 5),
                Row(
                  children: [
                    Icon(
                      Icons.event_outlined,
                      size: 15,
                      color: expiringSoon ? AppColors.error : AppColors.textSecondary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Hết hạn: ${AppFormatters.date.format(member.endDate)}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: expiringSoon ? AppColors.error : AppColors.textSecondary,
                            fontWeight: expiringSoon ? FontWeight.w700 : FontWeight.w500,
                          ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
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
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: Text(label, style: Theme.of(context).textTheme.bodySmall)),
          const SizedBox(width: 12),
          Flexible(
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
