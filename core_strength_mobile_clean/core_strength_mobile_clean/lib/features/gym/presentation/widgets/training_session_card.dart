import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../domain/entities/gym_entities.dart';

class TrainingSessionCard extends StatelessWidget {
  const TrainingSessionCard({
    super.key,
    required this.session,
    this.compact = false,
    this.onTap,
  });

  final TrainingSession session;
  final bool compact;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final statusType = switch (session.status) {
      SessionStatus.pending => StatusType.warning,
      SessionStatus.upcoming => StatusType.info,
      SessionStatus.completed => StatusType.success,
      SessionStatus.cancelled => StatusType.error,
      SessionStatus.noShow => StatusType.warning,
    };

    return AppCard(
      onTap: onTap,
      padding: EdgeInsets.all(compact ? 14 : 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 43,
                height: 43,
                decoration: BoxDecoration(
                  color: AppColors.primarySoft,
                  borderRadius: BorderRadius.circular(13),
                ),
                child: const Icon(
                  Icons.fitness_center_rounded,
                  color: AppColors.primary,
                  size: 21,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      session.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        height: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      session.participantName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              StatusChip(label: session.status.label, type: statusType),
            ],
          ),
          const SizedBox(height: 13),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: AppColors.surfaceMuted,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.divider),
            ),
            child: Row(
              children: [
                Expanded(
                  child: _Info(
                    icon: Icons.calendar_today_outlined,
                    text: AppFormatters.date.format(session.startAt),
                  ),
                ),
                Container(width: 1, height: 22, color: AppColors.divider),
                const SizedBox(width: 12),
                Expanded(
                  child: _Info(
                    icon: Icons.schedule_rounded,
                    text:
                        '${AppFormatters.time.format(session.startAt)} - ${AppFormatters.time.format(session.endAt)}',
                  ),
                ),
              ],
            ),
          ),
          if (session.location != null && session.location!.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            _Info(icon: Icons.place_outlined, text: session.location!),
          ],
          if (!compact && session.note != null && session.note!.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(session.note!, style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}

class _Info extends StatelessWidget {
  const _Info({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 15, color: AppColors.textSecondary),
        const SizedBox(width: 6),
        Flexible(
          child: Text(
            text,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
      ],
    );
  }
}
