import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

import '../../../auth/domain/entities/app_user.dart';
import 'history_page.dart';
import 'member_home_page.dart';
import 'profile_page.dart';
import 'qr_checkin_page.dart';
import 'schedule_page.dart';

class MemberShell extends StatefulWidget {
  const MemberShell({super.key, required this.user});

  final AppUser user;

  @override
  State<MemberShell> createState() => _MemberShellState();
}

class _MemberShellState extends State<MemberShell> {
  int _index = 0;

  void _goTo(int value) => setState(() => _index = value);

  @override
  Widget build(BuildContext context) {
    final pages = [
      MemberHomePage(user: widget.user, onNavigate: _goTo),
      SchedulePage(user: widget.user),
      QrCheckinPage(user: widget.user),
      HistoryPage(user: widget.user),
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
            label: 'Lịch tập',
          ),
          NavigationDestination(
            icon: Icon(Icons.qr_code_scanner_outlined),
            selectedIcon: Icon(Icons.qr_code_scanner_rounded),
            label: 'Check-in',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history_rounded),
            label: 'Lịch sử',
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
