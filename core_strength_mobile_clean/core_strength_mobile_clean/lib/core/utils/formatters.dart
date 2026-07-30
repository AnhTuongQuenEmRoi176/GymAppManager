import 'package:intl/intl.dart';

class AppFormatters {
  const AppFormatters._();

  static final DateFormat date = DateFormat('dd/MM/yyyy');
  static final DateFormat dateTime = DateFormat('HH:mm - dd/MM/yyyy');
  static final DateFormat time = DateFormat('HH:mm');
  static final NumberFormat currency = NumberFormat.currency(
    locale: 'vi_VN',
    symbol: '₫',
    decimalDigits: 0,
  );

  static String compactCurrency(num value) {
    if (value >= 1000000000) {
      return '${(value / 1000000000).toStringAsFixed(value % 1000000000 == 0 ? 0 : 1)} tỷ';
    }
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(value % 1000000 == 0 ? 0 : 1)} triệu';
    }
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(value % 1000 == 0 ? 0 : 1)} nghìn';
    }
    return value.toStringAsFixed(0);
  }
}
