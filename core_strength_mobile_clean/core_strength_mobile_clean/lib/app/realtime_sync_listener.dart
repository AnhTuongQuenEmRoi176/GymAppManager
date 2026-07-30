import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/realtime/realtime_event.dart';
import '../features/auth/domain/entities/app_user.dart';
import '../features/auth/presentation/providers/auth_provider.dart';
import '../features/gym/presentation/providers/gym_providers.dart';

class RealtimeSyncListener extends ConsumerStatefulWidget {
  const RealtimeSyncListener({
    super.key,
    required this.user,
    required this.child,
  });

  final AppUser user;
  final Widget child;

  @override
  ConsumerState<RealtimeSyncListener> createState() =>
      _RealtimeSyncListenerState();
}

class _RealtimeSyncListenerState extends ConsumerState<RealtimeSyncListener> {
  StreamSubscription<RealtimeEvent>? _subscription;

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      _subscription = ref.read(realtimeServiceProvider).events.listen(_handleEvent);
    });
  }

  void _handleEvent(RealtimeEvent event) {
    if (!mounted) return;

    switch (event.type) {
      case 'checkin.confirmed':
      case 'checkin_confirmed':
        ref.invalidate(checkinHistoryProvider);
        ref.invalidate(memberDashboardProvider);
        ref.invalidate(trainerDashboardProvider);
        ref.invalidate(notificationsProvider);
        break;
      case 'schedule.created':
      case 'schedule.updated':
      case 'schedule.cancelled':
        ref.invalidate(scheduleProvider(widget.user.role));
        ref.invalidate(memberDashboardProvider);
        ref.invalidate(trainerDashboardProvider);
        ref.invalidate(notificationsProvider);
        break;
      case 'membership.updated':
      case 'membership.sessions_changed':
        ref.invalidate(memberDashboardProvider);
        ref.invalidate(assignedMembersProvider);
        ref.invalidate(trainerDashboardProvider);
        ref.invalidate(notificationsProvider);
        break;
      case 'pt_session.created':
      case 'trainer.kpi_changed':
        ref.invalidate(trainerDashboardProvider);
        ref.invalidate(memberDashboardProvider);
        ref.invalidate(scheduleProvider(widget.user.role));
        ref.invalidate(notificationsProvider);
        break;
      case 'notification.created':
        ref.invalidate(notificationsProvider);
        break;
      default:
        break;
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
