import 'package:flutter/material.dart';

import 'app_colors.dart';

class AppInputTheme {

  static InputDecorationTheme theme =
      InputDecorationTheme(

    filled: true,

    fillColor: AppColors.surface,

    border: OutlineInputBorder(

      borderRadius:
      BorderRadius.circular(16),

      borderSide: BorderSide.none,

    ),

    focusedBorder:
    OutlineInputBorder(

      borderRadius:
      BorderRadius.circular(16),

      borderSide:
      const BorderSide(

        color: AppColors.primary,

        width: 2,

      ),

    ),

  );

}