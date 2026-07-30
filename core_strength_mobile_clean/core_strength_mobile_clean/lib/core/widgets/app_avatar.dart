import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class AppAvatar extends StatelessWidget {
  const AppAvatar({
    super.key,
    required this.name,
    this.imageUrl,
    this.size = 42,
    this.backgroundColor = AppColors.primarySoft,
    this.foregroundColor = AppColors.primary,
    this.borderColor,
  });

  final String name;
  final String? imageUrl;
  final double size;
  final Color backgroundColor;
  final Color foregroundColor;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    final url = imageUrl?.trim();
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor,
        shape: BoxShape.circle,
        border: Border.all(color: borderColor ?? backgroundColor, width: 1.5),
      ),
      clipBehavior: Clip.antiAlias,
      alignment: Alignment.center,
      child: url != null && url.isNotEmpty
          ? Image.network(
              url,
              width: size,
              height: size,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _Initials(
                name: name,
                color: foregroundColor,
                fontSize: size * 0.34,
              ),
            )
          : _Initials(
              name: name,
              color: foregroundColor,
              fontSize: size * 0.34,
            ),
    );
  }
}

class _Initials extends StatelessWidget {
  const _Initials({
    required this.name,
    required this.color,
    required this.fontSize,
  });

  final String name;
  final Color color;
  final double fontSize;

  @override
  Widget build(BuildContext context) {
    final parts = name.trim().split(RegExp(r'\s+')).where((part) => part.isNotEmpty).toList();
    final initials = parts.isEmpty
        ? 'CS'
        : parts.length == 1
            ? parts.first.substring(0, 1).toUpperCase()
            : '${parts.first.substring(0, 1)}${parts.last.substring(0, 1)}'.toUpperCase();
    return Text(
      initials,
      style: TextStyle(
        color: color,
        fontSize: fontSize,
        fontWeight: FontWeight.w900,
      ),
    );
  }

}
