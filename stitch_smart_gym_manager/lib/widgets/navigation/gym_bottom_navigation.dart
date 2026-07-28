import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class GymBottomNavigation extends StatelessWidget {

  final int currentIndex;

  final Function(int) onTap;

  const GymBottomNavigation({

    super.key,

    required this.currentIndex,

    required this.onTap,

  });

  @override
  Widget build(BuildContext context) {

    return NavigationBar(

      selectedIndex: currentIndex,

      backgroundColor: AppColors.surface,

      indicatorColor: AppColors.primary,

      labelBehavior:
      NavigationDestinationLabelBehavior.alwaysShow,

      onDestinationSelected: onTap,

      destinations: const [

        NavigationDestination(

          icon: Icon(Icons.home_outlined),

          selectedIcon: Icon(Icons.home),

          label: "Home",

        ),

        NavigationDestination(

          icon: Icon(Icons.calendar_month_outlined),

          selectedIcon: Icon(Icons.calendar_month),

          label: "Lịch",

        ),

        NavigationDestination(

          icon: Icon(Icons.qr_code_scanner),

          selectedIcon: Icon(Icons.qr_code),

          label: "QR",

        ),

        NavigationDestination(

          icon: Icon(Icons.person_outline),

          selectedIcon: Icon(Icons.person),

          label: "Tôi",

        ),

      ],

    );

  }

}