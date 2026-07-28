import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class PageContainer extends StatelessWidget {

  final Widget child;

  const PageContainer({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: AppColors.background,

      body: SafeArea(

        child: Center(

          child: SingleChildScrollView(

            padding: const EdgeInsets.all(24),

            child: child,

          ),

        ),

      ),

    );

  }
}