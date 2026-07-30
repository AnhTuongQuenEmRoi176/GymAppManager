import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/app_config.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../data/repositories/mock_gym_repository.dart';
import '../../data/repositories/remote_gym_repository.dart';
import '../../domain/entities/gym_entities.dart';
import '../../domain/repositories/gym_repository.dart';

final gymRepositoryProvider = Provider<GymRepository>((ref) {
  if (AppConfig.useMockData) return MockGymRepository();
  return RemoteGymRepository(ref.watch(apiClientProvider));
});

final memberDashboardProvider = FutureProvider<MemberDashboardData>((ref) {
  return ref.watch(gymRepositoryProvider).getMemberDashboard();
});

final trainerDashboardProvider = FutureProvider<TrainerDashboardData>((ref) {
  return ref.watch(gymRepositoryProvider).getTrainerDashboard();
});

final scheduleProvider = FutureProvider.family<List<TrainingSession>, UserRole>(
  (ref, role) => ref.watch(gymRepositoryProvider).getSchedule(role),
);

final checkinHistoryProvider = FutureProvider<List<CheckinRecord>>(
  (ref) => ref.watch(gymRepositoryProvider).getCheckinHistory(),
);

final assignedMembersProvider = FutureProvider<List<AssignedMember>>(
  (ref) => ref.watch(gymRepositoryProvider).getAssignedMembers(),
);

final notificationsProvider = FutureProvider<List<AppNotificationItem>>(
  (ref) => ref.watch(gymRepositoryProvider).getNotifications(),
);
