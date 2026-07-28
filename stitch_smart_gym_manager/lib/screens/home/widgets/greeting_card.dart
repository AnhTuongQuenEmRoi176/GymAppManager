import 'package:flutter/material.dart';

import '../../../core/theme/app_text_styles.dart';

class GreetingCard extends StatelessWidget {
  const GreetingCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [

        Text(
          "Xin chào 👋",
          style: AppTextStyles.bodyMedium,
        ),

        const SizedBox(height: 8),

        Text(
          "Sơn",
          style: AppTextStyles.headlineLarge,
        ),

      ],
    );
  }
}