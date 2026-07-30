import '../../../auth/domain/entities/app_user.dart';
import '../entities/gym_entities.dart';

abstract class GymRepository {
  Future<MemberDashboardData> getMemberDashboard();
  Future<TrainerDashboardData> getTrainerDashboard();
  Future<List<TrainingSession>> getSchedule(UserRole role);
  Future<void> createSchedule(ScheduleCreateInput input);
  Future<void> updateSchedule(int scheduleId, ScheduleUpdateInput input);
  Future<void> cancelSchedule(int scheduleId);
  Future<List<CheckinRecord>> getCheckinHistory();
  Future<List<AssignedMember>> getAssignedMembers();
  Future<List<AppNotificationItem>> getNotifications();
  Future<QrToken> createQrToken(UserRole role);
}
