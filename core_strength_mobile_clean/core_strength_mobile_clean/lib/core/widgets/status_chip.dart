import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

enum StatusType { success, warning, error, info, neutral }

class StatusChip extends StatelessWidget {
  const StatusChip({
    super.key,
    required this.label,
    this.type = StatusType.neutral,
    this.icon,
  });

  final String label;
  final StatusType type;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final config = switch (type) {
      StatusType.success => (AppColors.successSoft, AppColors.successBorder, AppColors.success),
      StatusType.warning => (AppColors.warningSoft, AppColors.warningBorder, AppColors.warning),
      StatusType.error => (AppColors.errorSoft, AppColors.errorBorder, AppColors.error),
      StatusType.info => (AppColors.infoSoft, AppColors.primaryBorder, AppColors.info),
      StatusType.neutral => (AppColors.surfaceMuted, AppColors.border, AppColors.textSecondary),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: config.$1,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: config.$2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 13, color: config.$3),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: config.$3,
              fontSize: 11,
              fontWeight: FontWeight.w800,
              height: 1,
            ),
          ),
        ],
      ),
    );
  }
}
