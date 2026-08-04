import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../../core/config/app_config.dart';
import '../../../../core/realtime/realtime_event.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_header.dart';
import '../../../../core/widgets/app_message_banner.dart';
import '../../../../core/widgets/status_chip.dart';
import '../../../auth/domain/entities/app_user.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';
import 'notifications_page.dart';

class QrCheckinPage extends ConsumerStatefulWidget {
  const QrCheckinPage({super.key, required this.user});

  final AppUser user;

  @override
  ConsumerState<QrCheckinPage> createState() => _QrCheckinPageState();
}

class _QrCheckinPageState extends ConsumerState<QrCheckinPage> {
  QrToken? _token;
  Timer? _timer;
  int _remainingSeconds = 0;
  bool _loading = true;
  bool _confirmed = false;
  String? _error;
  StreamSubscription<RealtimeEvent>? _eventSubscription;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      await _loadToken();
      _eventSubscription = ref
          .read(realtimeServiceProvider)
          .events
          .listen(_onEvent);
    });
  }

  void _onEvent(RealtimeEvent event) {
    if (!mounted) return;
    if (event.type == 'checkin.confirmed' ||
        event.type == 'checkin_confirmed') {
      setState(() => _confirmed = true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Check-in đã được lễ tân xác nhận.')),
      );
    }
  }

  Future<void> _loadToken() async {
    _timer?.cancel();
    if (mounted) {
      setState(() {
        _loading = true;
        _error = null;
        _confirmed = false;
      });
    }

    try {
      final token = await ref
          .read(gymRepositoryProvider)
          .createQrToken(widget.user.role);
      if (!mounted) return;
      setState(() {
        _token = token;
        _remainingSeconds = token.expiresAt
            .difference(DateTime.now())
            .inSeconds
            .clamp(0, 999)
            .toInt();
        _loading = false;
      });
      _startCountdown();
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  void _startCountdown() {
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || _token == null) return;
      final remaining = _token!.expiresAt.difference(DateTime.now()).inSeconds;
      if (remaining <= 0) {
        _timer?.cancel();
        setState(() => _remainingSeconds = 0);
        Future<void>.delayed(const Duration(milliseconds: 350), _loadToken);
        return;
      }
      setState(() => _remainingSeconds = remaining);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _eventSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final status = _confirmed
        ? const StatusChip(
            label: 'Đã xác nhận',
            type: StatusType.success,
            icon: Icons.check_rounded,
          )
        : StatusChip(
            label: _remainingSeconds > 0
                ? 'Sẵn sàng · $_remainingSeconds giây'
                : 'Đang làm mới',
            type: _remainingSeconds > 0
                ? StatusType.success
                : StatusType.neutral,
            icon: Icons.qr_code_2_rounded,
          );

    return SafeArea(
      child: ListView(
        padding: AppLayout.pageInsets,
        children: [
          AppHeader(
            name: widget.user.fullName,
            subtitle: widget.user.role.label,
            avatarUrl: widget.user.avatarUrl,
            onNotifications: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => const NotificationsPage(),
              ),
            ),
          ),
          const SizedBox(height: 18),
          Text(
            'Quét mã Check-in',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 5),
          Text(
            'Đưa mã QR này cho lễ tân để xác nhận vào phòng tập.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          AppCard(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Mã QR cá nhân',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    status,
                  ],
                ),
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _confirmed
                          ? AppColors.successBorder
                          : AppColors.divider,
                      width: _confirmed ? 1.5 : 1,
                    ),
                  ),
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: Center(child: _buildQr()),
                  ),
                ),
                const SizedBox(height: 14),
                ClipRRect(
                  borderRadius: BorderRadius.circular(99),
                  child: LinearProgressIndicator(
                    value: _remainingSeconds <= 0
                        ? 0
                        : (_remainingSeconds / 30).clamp(0.0, 1.0).toDouble(),
                    minHeight: 6,
                    backgroundColor: AppColors.divider,
                    color: _confirmed ? AppColors.success : AppColors.primary,
                  ),
                ),
                const SizedBox(height: 7),
                Text(
                  _confirmed
                      ? 'Lễ tân đã xác nhận mã của bạn.'
                      : 'Mã sẽ tự động thay đổi để bảo đảm an toàn.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          const SizedBox(height: AppLayout.cardGap),
          AppCard(
            child: Row(
              children: [
                AppAvatar(
                  name: widget.user.fullName,
                  imageUrl: widget.user.avatarUrl,
                  size: 44,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.user.fullName,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        widget.user.role.label,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons.verified_user_outlined,
                  color: AppColors.primary,
                  size: 21,
                ),
              ],
            ),
          ),
          const SizedBox(height: AppLayout.cardGap),
          OutlinedButton.icon(
            onPressed: _loading ? null : _loadToken,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Tạo mã mới'),
          ),
          const SizedBox(height: AppLayout.cardGap),
          AppMessageBanner(
            title: 'Lưu ý bảo mật',
            message: AppConfig.useMockData
                ? 'Ứng dụng đang chạy dữ liệu demo. Khi dùng API thật, mã QR được ký số, hết hạn tự động và chỉ dùng một lần.'
                : 'Không chụp hoặc chia sẻ mã QR. Mã sẽ hết hạn và được làm mới tự động.',
            type: AppMessageType.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildQr() {
    if (_loading) {
      return const SizedBox(
        width: 30,
        height: 30,
        child: CircularProgressIndicator(strokeWidth: 2.2),
      );
    }

    if (_error != null || _token == null || _token!.value.isEmpty) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.qr_code_2_rounded,
            size: 68,
            color: AppColors.textMuted,
          ),
          const SizedBox(height: 12),
          Text(
            _error ?? 'Không tạo được mã QR.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 12),
          FilledButton.tonal(
            onPressed: _loadToken,
            child: const Text('Thử lại'),
          ),
        ],
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final size = constraints.maxWidth.clamp(180.0, 240.0).toDouble();
        return QrImageView(
          data: _token!.value,
          version: QrVersions.auto,
          size: size,
          gapless: true,
          backgroundColor: Colors.white,
          padding: const EdgeInsets.all(8),
          eyeStyle: const QrEyeStyle(
            eyeShape: QrEyeShape.square,
            color: Colors.black,
          ),
          dataModuleStyle: const QrDataModuleStyle(
            dataModuleShape: QrDataModuleShape.square,
            color: Colors.black,
          ),
        );
      },
    );
  }
}
