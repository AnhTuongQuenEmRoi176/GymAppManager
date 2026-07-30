import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

import '../../../auth/domain/entities/app_user.dart';
import 'profile_page.dart';
import 'qr_checkin_page.dart';
import 'schedule_page.dart';
import 'trainer_home_page.dart';
import 'trainer_members_page.dart';

class TrainerShell extends StatefulWidget {
  const TrainerShell({super.key, required this.user});

  final AppUser user;

  @override
  State<TrainerShell> createState() => _TrainerShellState();
}

class _TrainerShellState extends State<TrainerShell> {
  int _index = 0;

  void _goTo(int value) => setState(() => _index = value);

  @override
  Widget build(BuildContext context) {
    final pages = [
      TrainerHomePage(user: widget.user, onNavigate: _goTo),
      SchedulePage(user: widget.user),
      QrCheckinPage(user: widget.user),
      TrainerMembersPage(user: widget.user),
      ProfilePage(user: widget.user),
    ];

    return Scaffold(
      body: IndexedStack(index: _index, children: pages),
      bottomNavigationBar: DecoratedBox(
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(top: BorderSide(color: AppColors.border)),
        ),
        child: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: _goTo,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'Trang chủ',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month_rounded),
            label: 'Lịch dạy',
          ),
          NavigationDestination(
            icon: Icon(Icons.qr_code_scanner_outlined),
            selectedIcon: Icon(Icons.qr_code_scanner_rounded),
            label: 'Check-in',
          ),
          NavigationDestination(
            icon: Icon(Icons.groups_2_outlined),
            selectedIcon: Icon(Icons.groups_2_rounded),
            label: 'Hội viên',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'Cá nhân',
          ),
        ],
        ),
      ),
    );
  }
}
