class RealtimeEvent {
  const RealtimeEvent({
    required this.type,
    required this.payload,
    required this.receivedAt,
  });

  final String type;
  final Map<String, dynamic> payload;
  final DateTime receivedAt;

  factory RealtimeEvent.fromJson(Map<String, dynamic> json) {
    return RealtimeEvent(
      type: json['type']?.toString() ?? 'unknown',
      payload: (json['payload'] as Map?)?.cast<String, dynamic>() ??
          <String, dynamic>{},
      receivedAt: DateTime.tryParse(json['received_at']?.toString() ?? '') ??
          DateTime.now(),
    );
  }
}
