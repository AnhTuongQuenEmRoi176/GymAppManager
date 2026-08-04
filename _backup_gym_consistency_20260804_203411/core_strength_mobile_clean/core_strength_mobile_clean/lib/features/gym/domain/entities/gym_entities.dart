import '../../../auth/domain/entities/app_user.dart';

enum SessionStatus {
  pending,
  upcoming,
  completed,
  cancelled,
  noShow;

  String get label => switch (this) {
        SessionStatus.pending => 'Chờ xác nhận',
        SessionStatus.upcoming => 'Sắp diễn ra',
        SessionStatus.completed => 'Hoàn thành',
        SessionStatus.cancelled => 'Đã hủy',
        SessionStatus.noShow => 'Vắng mặt',
      };

  bool get canBeChanged =>
      this == SessionStatus.pending || this == SessionStatus.upcoming;

  static SessionStatus fromValue(String? value) {
    return switch (value?.toLowerCase()) {
      'pending' => SessionStatus.pending,
      'completed' || 'done' => SessionStatus.completed,
      'cancelled' || 'canceled' => SessionStatus.cancelled,
      'no_show' || 'noshow' => SessionStatus.noShow,
      _ => SessionStatus.upcoming,
    };
  }
}

class MembershipSummary {
  const MembershipSummary({
    required this.packageName,
    required this.startDate,
    required this.endDate,
    required this.sessionsRemaining,
    required this.progress,
    this.trainerName,
    this.status = 'Còn hạn',
  });

  final String packageName;
  final DateTime startDate;
  final DateTime endDate;
  final int? sessionsRemaining;
  final double progress;
  final String? trainerName;
  final String status;
}

class TrainingSession {
  const TrainingSession({
    required this.id,
    required this.title,
    required this.participantName,
    required this.startAt,
    required this.endAt,
    required this.status,
    this.location,
    this.note,
  });

  final int id;
  final String title;
  final String participantName;
  final DateTime startAt;
  final DateTime endAt;
  final SessionStatus status;
  final String? location;
  final String? note;
}

class ScheduleCreateInput {
  const ScheduleCreateInput({
    required this.memberId,
    required this.memberPackageId,
    required this.title,
    required this.startAt,
    required this.endAt,
    this.location,
    this.note,
  });

  final int memberId;
  final int memberPackageId;
  final String title;
  final DateTime startAt;
  final DateTime endAt;
  final String? location;
  final String? note;
}

class ScheduleUpdateInput {
  const ScheduleUpdateInput({
    required this.title,
    required this.startAt,
    required this.endAt,
    this.location,
    this.note,
  });

  final String title;
  final DateTime startAt;
  final DateTime endAt;
  final String? location;
  final String? note;
}

class ActivityItem {
  const ActivityItem({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.occurredAt,
    required this.type,
  });

  final int id;
  final String title;
  final String subtitle;
  final DateTime occurredAt;
  final String type;
}

class MemberDashboardData {
  const MemberDashboardData({
    required this.membership,
    required this.upcomingSessions,
    required this.recentActivities,
    required this.monthlyCheckins,
  });

  final MembershipSummary membership;
  final List<TrainingSession> upcomingSessions;
  final List<ActivityItem> recentActivities;
  final int monthlyCheckins;
}

class TrainerStats {
  const TrainerStats({
    required this.todaySessions,
    required this.assignedMembers,
    required this.monthlySessions,
    required this.estimatedIncome,
  });

  final int todaySessions;
  final int assignedMembers;
  final int monthlySessions;
  final double estimatedIncome;
}

class MemberAlert {
  const MemberAlert({
    required this.memberName,
    required this.message,
    required this.severity,
    this.sessionsRemaining,
  });

  final String memberName;
  final String message;
  final String severity;
  final int? sessionsRemaining;
}

class TrainerDashboardData {
  const TrainerDashboardData({
    required this.stats,
    required this.todaySessions,
    required this.alerts,
    required this.isWorking,
  });

  final TrainerStats stats;
  final List<TrainingSession> todaySessions;
  final List<MemberAlert> alerts;
  final bool isWorking;
}

class CheckinRecord {
  const CheckinRecord({
    required this.id,
    required this.scannedAt,
    required this.location,
    required this.status,
    required this.source,
  });

  final int id;
  final DateTime scannedAt;
  final String location;
  final String status;
  final String source;
}

class QrToken {
  const QrToken({
    required this.value,
    required this.expiresAt,
    required this.entityType,
  });

  final String value;
  final DateTime expiresAt;
  final UserRole entityType;
}

class AssignedMember {
  const AssignedMember({
    required this.id,
    required this.memberPackageId,
    required this.fullName,
    required this.packageName,
    required this.endDate,
    required this.sessionsRemaining,
    required this.phone,
  });

  final int id;
  final int memberPackageId;
  final String fullName;
  final String packageName;
  final DateTime endDate;
  final int sessionsRemaining;
  final String phone;
}

class AppNotificationItem {
  const AppNotificationItem({
    required this.id,
    required this.title,
    required this.body,
    required this.createdAt,
    required this.type,
    this.isRead = false,
  });

  final int id;
  final String title;
  final String body;
  final DateTime createdAt;
  final String type;
  final bool isRead;
}
