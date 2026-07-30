import 'dart:async';

import '../../../auth/domain/entities/app_user.dart';
import '../../domain/entities/gym_entities.dart';
import '../../domain/repositories/gym_repository.dart';

class MockGymRepository implements GymRepository {
  DateTime get _now => DateTime.now();

  Future<T> _delay<T>(T value) async {
    await Future<void>.delayed(const Duration(milliseconds: 420));
    return value;
  }

  @override
  Future<MemberDashboardData> getMemberDashboard() {
    final now = _now;
    return _delay(
      MemberDashboardData(
        membership: MembershipSummary(
          packageName: 'Gói GYM Gold',
          startDate: now.subtract(const Duration(days: 62)),
          endDate: now.add(const Duration(days: 28)),
          sessionsRemaining: 12,
          progress: 0.75,
          trainerName: 'PT Minh Quân',
        ),
        monthlyCheckins: 9,
        upcomingSessions: [
          TrainingSession(
            id: 1,
            title: 'Tập Ngực - Vai',
            participantName: 'PT Minh Quân',
            startAt: DateTime(now.year, now.month, now.day + 1, 18),
            endAt: DateTime(now.year, now.month, now.day + 1, 19, 30),
            status: SessionStatus.upcoming,
            location: 'Khu PT tầng 2',
          ),
          TrainingSession(
            id: 2,
            title: 'Cardio & Yoga',
            participantName: 'Tự tập',
            startAt: DateTime(now.year, now.month, now.day + 3, 17, 30),
            endAt: DateTime(now.year, now.month, now.day + 3, 18, 30),
            status: SessionStatus.upcoming,
            location: 'Phòng Cardio',
          ),
        ],
        recentActivities: [
          ActivityItem(
            id: 1,
            title: 'Check-in thành công',
            subtitle: 'Lễ tân xác nhận tại Quầy chính',
            occurredAt: now.subtract(const Duration(hours: 2)),
            type: 'checkin',
          ),
          ActivityItem(
            id: 2,
            title: 'Hoàn thành buổi tập',
            subtitle: 'Tập lưng - xô cùng PT Minh Quân',
            occurredAt: now.subtract(const Duration(days: 1)),
            type: 'session',
          ),
          ActivityItem(
            id: 3,
            title: 'Gia hạn gói Gold',
            subtitle: 'Thanh toán thành công qua lễ tân',
            occurredAt: now.subtract(const Duration(days: 3)),
            type: 'payment',
          ),
        ],
      ),
    );
  }

  @override
  Future<TrainerDashboardData> getTrainerDashboard() {
    final now = _now;
    return _delay(
      TrainerDashboardData(
        stats: const TrainerStats(
          todaySessions: 5,
          assignedMembers: 12,
          monthlySessions: 80,
          estimatedIncome: 12500000,
        ),
        isWorking: true,
        todaySessions: [
          TrainingSession(
            id: 10,
            title: 'Train T1-B',
            participantName: 'Võ Ngọc An',
            startAt: DateTime(now.year, now.month, now.day, 10),
            endAt: DateTime(now.year, now.month, now.day, 11, 30),
            status: SessionStatus.upcoming,
            location: 'Khu PT tầng 1',
          ),
          TrainingSession(
            id: 11,
            title: 'Buổi tập cá nhân',
            participantName: 'Nguyễn Văn A',
            startAt: DateTime(now.year, now.month, now.day, 14, 30),
            endAt: DateTime(now.year, now.month, now.day, 15, 30),
            status: SessionStatus.upcoming,
            location: 'Khu PT tầng 2',
          ),
        ],
        alerts: const [
          MemberAlert(
            memberName: 'Lê Hoàng Nam',
            message: 'Sắp hết buổi tập, còn 2 buổi',
            severity: 'warning',
            sessionsRemaining: 2,
          ),
          MemberAlert(
            memberName: 'Trần Thu Hà',
            message: 'Gói tập sẽ hết hạn trong 5 ngày',
            severity: 'danger',
          ),
        ],
      ),
    );
  }

  @override
  Future<List<TrainingSession>> getSchedule(UserRole role) {
    final now = _now;
    final participant = role == UserRole.member ? 'PT Minh Quân' : 'Nguyễn Văn A';
    return _delay([
      TrainingSession(
        id: 21,
        title: "Tập Ngực (Chest Day)",
        participantName: participant,
        startAt: DateTime(now.year, now.month, now.day, 17, 30),
        endAt: DateTime(now.year, now.month, now.day, 19),
        status: SessionStatus.upcoming,
        location: 'Khu tập chính',
        note: 'Ưu tiên bài đẩy ngực và vai trước.',
      ),
      TrainingSession(
        id: 22,
        title: 'Tập Chân (Leg Day)',
        participantName: participant,
        startAt: DateTime(now.year, now.month, now.day - 1, 16),
        endAt: DateTime(now.year, now.month, now.day - 1, 17, 30),
        status: SessionStatus.completed,
        location: 'Khu PT tầng 2',
      ),
      TrainingSession(
        id: 23,
        title: 'Cardio & Yoga',
        participantName: role == UserRole.member ? 'Tự tập' : 'Lê Hoàng Nam',
        startAt: DateTime(now.year, now.month, now.day + 4, 7),
        endAt: DateTime(now.year, now.month, now.day + 4, 8),
        status: SessionStatus.cancelled,
        location: 'Phòng Cardio',
      ),
      TrainingSession(
        id: 24,
        title: 'Tập Lưng - Xô',
        participantName: participant,
        startAt: DateTime(now.year, now.month, now.day + 6, 18),
        endAt: DateTime(now.year, now.month, now.day + 6, 19, 30),
        status: SessionStatus.upcoming,
        location: 'Khu tập chính',
      ),
    ]);
  }

  @override
  Future<void> createSchedule(ScheduleCreateInput input) async {
    await Future<void>.delayed(const Duration(milliseconds: 420));
  }

  @override
  Future<void> updateSchedule(
    int scheduleId,
    ScheduleUpdateInput input,
  ) async {
    await Future<void>.delayed(const Duration(milliseconds: 420));
  }

  @override
  Future<void> cancelSchedule(int scheduleId) async {
    await Future<void>.delayed(const Duration(milliseconds: 420));
  }

  @override
  Future<List<CheckinRecord>> getCheckinHistory() {
    final now = _now;
    return _delay(List.generate(
      8,
      (index) => CheckinRecord(
        id: index + 1,
        scannedAt: now.subtract(Duration(days: index * 2, hours: index)),
        location: index.isEven ? 'Quầy check-in chính' : 'Cổng phụ tầng 1',
        status: 'Thành công',
        source: index.isEven ? 'QR Mobile' : 'Xác nhận lễ tân',
      ),
    ));
  }

  @override
  Future<List<AssignedMember>> getAssignedMembers() {
    final now = _now;
    return _delay([
      AssignedMember(
        id: 1,
        memberPackageId: 101,
        fullName: 'Nguyễn Văn A',
        packageName: 'Gold + PT 30 buổi',
        endDate: now.add(const Duration(days: 28)),
        sessionsRemaining: 12,
        phone: '0987 654 321',
      ),
      AssignedMember(
        id: 2,
        memberPackageId: 102,
        fullName: 'Lê Hoàng Nam',
        packageName: 'Premium + PT 10 buổi',
        endDate: now.add(const Duration(days: 9)),
        sessionsRemaining: 2,
        phone: '0966 112 233',
      ),
      AssignedMember(
        id: 3,
        memberPackageId: 103,
        fullName: 'Trần Thu Hà',
        packageName: 'Gold + PT 50 buổi',
        endDate: now.add(const Duration(days: 5)),
        sessionsRemaining: 24,
        phone: '0904 555 890',
      ),
      AssignedMember(
        id: 4,
        memberPackageId: 104,
        fullName: 'Võ Ngọc An',
        packageName: 'Silver + PT 30 buổi',
        endDate: now.add(const Duration(days: 44)),
        sessionsRemaining: 18,
        phone: '0936 778 899',
      ),
    ]);
  }

  @override
  Future<List<AppNotificationItem>> getNotifications() {
    final now = _now;
    return _delay([
      AppNotificationItem(
        id: 1,
        title: 'Check-in thành công',
        body: 'Buổi check-in lúc 18:05 đã được lễ tân xác nhận.',
        createdAt: now.subtract(const Duration(minutes: 12)),
        type: 'checkin',
      ),
      AppNotificationItem(
        id: 2,
        title: 'Lịch tập được cập nhật',
        body: 'Buổi Tập Ngực - Vai được chuyển sang 18:00 ngày mai.',
        createdAt: now.subtract(const Duration(hours: 3)),
        type: 'schedule',
      ),
      AppNotificationItem(
        id: 3,
        title: 'Gói tập sắp hết hạn',
        body: 'Gói GYM Gold còn 28 ngày. Liên hệ lễ tân để gia hạn.',
        createdAt: now.subtract(const Duration(days: 1)),
        type: 'membership',
        isRead: true,
      ),
    ]);
  }

  @override
  Future<QrToken> createQrToken(UserRole role) {
    final now = _now;
    return _delay(
      QrToken(
        value: 'CORE_STRENGTH|${role.apiValue}|${now.millisecondsSinceEpoch}|DEMO_SIGNATURE',
        expiresAt: now.add(const Duration(seconds: 30)),
        entityType: role,
      ),
    );
  }
}
