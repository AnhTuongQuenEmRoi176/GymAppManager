import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';

class LoginCard extends StatelessWidget {

  final Widget child;

  const LoginCard({

    super.key,

    required this.child,

  });

  @override
  Widget build(BuildContext context) {

    return Container(

      constraints: const BoxConstraints(

        maxWidth: 420,

      ),

      padding: const EdgeInsets.all(24),

      decoration: BoxDecoration(

        color: AppColors.surface,

        borderRadius:
            BorderRadius.circular(
                AppRadius.lg),

        border: Border.all(

          color: AppColors.border,

        ),

      ),

      child: child,

    );

  }
}