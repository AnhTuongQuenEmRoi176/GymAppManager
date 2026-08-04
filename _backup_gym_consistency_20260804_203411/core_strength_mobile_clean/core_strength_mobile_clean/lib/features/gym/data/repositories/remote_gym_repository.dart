import '../../../../core/network/api_client.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../../domain/repositories/gym_repository.dart';

class RemoteGymRepository implements GymRepository {
  const RemoteGymRepository(this._client);

  final ApiClient _client;

  @override
  Future<MemberDashboardData> getMemberDashboard() async {
    final json = await _client.getJson('/member/dashboard');
    final membershipJson = (json['membership'] as Map?)?.cast<String, dynamic>() ??
        <String, dynamic>{};
    return MemberDashboardData(
      membership: _parseMembership(membershipJson),
      monthlyCheckins: _asInt(json['monthly_checkins']),
      upcomingSessions: _parseSessions(json['upcoming_sessions']),
      recentActivities: _parseActivities(json['recent_activities']),
    );
  }

  @override
  Future<TrainerDashboardData> getTrainerDashboard() async {
    final json = await _client.getJson('/trainer/dashboard');
    final stats = (json['stats'] as Map?)?.cast<String, dynamic>() ??
        <String, dynamic>{};
    final alerts = (json['alerts'] as List? ?? const <dynamic>[])
        .whereType<Map>()
        .map((item) {
      final map = item.cast<String, dynamic>();
      return MemberAlert(
        memberName: map['member_name']?.toString() ?? 'Hội viên',
        message: map['message']?.toString() ?? '',
        severity: map['severity']?.toString() ?? 'warning',
        sessionsRemaining: map['sessions_remaining'] == null
            ? null
            : _asInt(map['sessions_remaining']),
      );
    }).toList();

    return TrainerDashboardData(
      stats: TrainerStats(
        todaySessions: _asInt(stats['today_sessions']),
        assignedMembers: _asInt(stats['assigned_members']),
        monthlySessions: _asInt(stats['monthly_sessions']),
        estimatedIncome: _asDouble(stats['estimated_income']),
      ),
      todaySessions: _parseSessions(json['today_sessions']),
      alerts: alerts,
      isWorking: json['is_working'] == true,
    );
  }

  @override
  Future<List<TrainingSession>> getSchedule(UserRole role) async {
    final list = await _client.getList('/schedules', queryParameters: {
      'role': role.apiValue,
    });
    return _parseSessions(list);
  }

  @override
  Future<void> createSchedule(ScheduleCreateInput input) async {
    await _client.postJson(
      '/schedules',
      data: {
        'member_id': input.memberId,
        'member_package_id': input.memberPackageId,
        'title': input.title.trim(),
        'start_at': input.startAt.toIso8601String(),
        'end_at': input.endAt.toIso8601String(),
        'location': _nullableText(input.location),
        'note': _nullableText(input.note),
      },
    );
  }

  @override
  Future<void> updateSchedule(
    int scheduleId,
    ScheduleUpdateInput input,
  ) async {
    await _client.patchJson(
      '/schedules/$scheduleId',
      data: {
        'title': input.title.trim(),
        'start_at': input.startAt.toIso8601String(),
        'end_at': input.endAt.toIso8601String(),
        'location': _nullableText(input.location),
        'note': _nullableText(input.note),
      },
    );
  }

  @override
  Future<void> cancelSchedule(int scheduleId) async {
    await _client.patchJson(
      '/schedules/$scheduleId',
      data: const {'status': 'cancelled'},
    );
  }

  @override
  Future<List<CheckinRecord>> getCheckinHistory() async {
    final list = await _client.getList('/checkins/history');
    return list.whereType<Map>().map((item) {
      final map = item.cast<String, dynamic>();
      return CheckinRecord(
        id: _asInt(map['id']),
        scannedAt: _asDate(map['scanned_at']),
        location: map['location']?.toString() ?? 'Phòng Gym',
        status: map['status']?.toString() ?? 'Thành công',
        source: map['source']?.toString() ?? 'QR Mobile',
      );
    }).toList();
  }

  @override
  Future<List<AssignedMember>> getAssignedMembers() async {
    final list = await _client.getList('/trainer/members');
    return list.whereType<Map>().map((item) {
      final map = item.cast<String, dynamic>();
      return AssignedMember(
        id: _asInt(map['id']),
        memberPackageId: _asInt(map['member_package_id']),
        fullName: map['full_name']?.toString() ?? 'Hội viên',
        packageName: map['package_name']?.toString() ?? 'Chưa có gói',
        endDate: _asDate(map['end_date']),
        sessionsRemaining: _asInt(map['sessions_remaining']),
        phone: map['phone']?.toString() ?? '',
      );
    }).toList();
  }

  @override
  Future<List<AppNotificationItem>> getNotifications() async {
    final list = await _client.getList('/notifications');
    return list.whereType<Map>().map((item) {
      final map = item.cast<String, dynamic>();
      return AppNotificationItem(
        id: _asInt(map['id']),
        title: map['title']?.toString() ?? 'Thông báo',
        body: map['body']?.toString() ?? '',
        createdAt: _asDate(map['created_at']),
        type: map['type']?.toString() ?? 'general',
        isRead: map['is_read'] == true,
      );
    }).toList();
  }

  @override
  Future<QrToken> createQrToken(UserRole role) async {
    final json = await _client.postJson(
      '/qr/token',
      data: {'entity_type': role.apiValue},
    );
    return QrToken(
      value: json['token']?.toString() ?? '',
      expiresAt: _asDate(json['expires_at']),
      entityType: role,
    );
  }

  MembershipSummary _parseMembership(Map<String, dynamic> map) {
    return MembershipSummary(
      packageName: map['package_name']?.toString() ?? 'Chưa có gói',
      startDate: _asDate(map['start_date']),
      endDate: _asDate(map['end_date']),
      sessionsRemaining: map['sessions_remaining'] == null
          ? null
          : _asInt(map['sessions_remaining']),
      progress: _asDouble(map['progress']).clamp(0.0, 1.0).toDouble(),
      trainerName: map['trainer_name']?.toString(),
      status: map['status']?.toString() ?? 'Còn hạn',
    );
  }

  List<TrainingSession> _parseSessions(dynamic value) {
    final list = value is List ? value : const <dynamic>[];
    return list.whereType<Map>().map((item) {
      final map = item.cast<String, dynamic>();
      return TrainingSession(
        id: _asInt(map['id']),
        title: map['title']?.toString() ?? 'Buổi tập',
        participantName: map['participant_name']?.toString() ??
            map['trainer_name']?.toString() ??
            map['member_name']?.toString() ??
            '',
        startAt: _asDate(map['start_at'] ?? map['session_date']),
        endAt: _asDate(map['end_at'] ?? map['session_date']),
        status: SessionStatus.fromValue(map['status']?.toString()),
        location: map['location']?.toString(),
        note: map['note']?.toString(),
      );
    }).toList();
  }

  List<ActivityItem> _parseActivities(dynamic value) {
    final list = value is List ? value : const <dynamic>[];
    return list.whereType<Map>().map((item) {
      final map = item.cast<String, dynamic>();
      return ActivityItem(
        id: _asInt(map['id']),
        title: map['title']?.toString() ?? 'Hoạt động',
        subtitle: map['subtitle']?.toString() ?? '',
        occurredAt: _asDate(map['occurred_at']),
        type: map['type']?.toString() ?? 'general',
      );
    }).toList();
  }

  static String? _nullableText(String? value) {
    final normalized = value?.trim();
    return normalized == null || normalized.isEmpty ? null : normalized;
  }

  static int _asInt(dynamic value) => int.tryParse(value?.toString() ?? '') ?? 0;
  static double _asDouble(dynamic value) =>
      double.tryParse(value?.toString() ?? '') ?? 0;
  static DateTime _asDate(dynamic value) =>
      DateTime.tryParse(value?.toString() ?? '') ?? DateTime.now();
}
