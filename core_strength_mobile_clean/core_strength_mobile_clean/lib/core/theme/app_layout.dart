import 'package:flutter/material.dart';

class AppLayout {
  const AppLayout._();

  static const double pagePadding = 16;
  static const double pageTopPadding = 14;
  static const double pageBottomPadding = 28;
  static const double sectionGap = 20;
  static const double cardGap = 12;
  static const double cardRadius = 16;
  static const double controlRadius = 13;
  static const double compactRadius = 11;
  static const double maxMobileWidth = 520;

  static const EdgeInsets pageInsets = EdgeInsets.fromLTRB(
    pagePadding,
    pageTopPadding,
    pagePadding,
    pageBottomPadding,
  );

  static const EdgeInsets cardInsets = EdgeInsets.all(16);
}
