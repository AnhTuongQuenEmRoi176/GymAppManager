import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_config.dart';
import '../storage/token_storage.dart';
import 'realtime_event.dart';

class RealtimeService {
  RealtimeService({required TokenStorage tokenStorage})
      : _tokenStorage = tokenStorage;

  final TokenStorage _tokenStorage;
  final StreamController<RealtimeEvent> _events =
      StreamController<RealtimeEvent>.broadcast();

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  Stream<RealtimeEvent> get events => _events.stream;

  Future<void> connect() async {
    await disconnect();
    if (AppConfig.useMockData) return;
    final token = await _tokenStorage.readAccessToken();
    if (token == null || token.isEmpty) return;

    final separator = AppConfig.webSocketUrl.contains('?') ? '&' : '?';
    final uri = Uri.parse(
      '${AppConfig.webSocketUrl}${separator}token=${Uri.encodeQueryComponent(token)}',
    );
    _channel = WebSocketChannel.connect(uri);
    _subscription = _channel!.stream.listen(
      (dynamic message) {
        try {
          final decoded = jsonDecode(message.toString());
          if (decoded is Map<String, dynamic>) {
            _events.add(RealtimeEvent.fromJson(decoded));
          }
        } catch (_) {
          _events.add(
            RealtimeEvent(
              type: 'raw_message',
              payload: {'message': message.toString()},
              receivedAt: DateTime.now(),
            ),
          );
        }
      },
      onError: (_) {},
      cancelOnError: false,
    );
  }

  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
  }

  Future<void> dispose() async {
    await disconnect();
    await _events.close();
  }
}
