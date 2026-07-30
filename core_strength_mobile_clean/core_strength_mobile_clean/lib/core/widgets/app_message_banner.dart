import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class AppMessageBanner extends StatelessWidget {
  const AppMessageBanner({
    super.key,
    required this.message,
    this.title,
    this.type = AppMessageType.info,
    this.onDismiss,
  });

  final String message;
  final String? title;
  final AppMessageType type;
  final VoidCallback? onDismiss;

  @override
  Widget build(BuildContext context) {
    final config = switch (type) {
      AppMessageType.info => (
          AppColors.infoSoft,
          AppColors.primaryBorder,
          AppColors.info,
          Icons.info_outline_rounded,
        ),
      AppMessageType.success => (
          AppColors.successSoft,
          AppColors.successBorder,
          AppColors.success,
          Icons.check_circle_outline_rounded,
        ),
      AppMessageType.warning => (
          AppColors.warningSoft,
          AppColors.warningBorder,
          AppColors.warning,
          Icons.warning_amber_rounded,
        ),
      AppMessageType.error => (
          AppColors.errorSoft,
          AppColors.errorBorder,
          AppColors.error,
          Icons.error_outline_rounded,
        ),
    };

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: config.$1,
        borderRadius: BorderRadius.circular(13),
        border: Border.all(color: config.$2),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(config.$4, size: 20, color: config.$3),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (title != null) ...[
                  Text(
                    title!,
                    style: TextStyle(
                      color: config.$3,
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 3),
                ],
                Text(
                  message,
                  style: TextStyle(
                    color: config.$3,
                    fontSize: 12,
                    height: 1.42,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          if (onDismiss != null) ...[
            const SizedBox(width: 6),
            InkWell(
              onTap: onDismiss,
              borderRadius: BorderRadius.circular(20),
              child: Padding(
                padding: const EdgeInsets.all(2),
                child: Icon(Icons.close_rounded, size: 18, color: config.$3),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

enum AppMessageType { info, success, warning, error }
