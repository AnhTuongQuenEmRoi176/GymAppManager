import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';

class GymFormField extends StatelessWidget {

  final TextEditingController controller;

  final String hint;

  final IconData icon;

  final bool obscure;

  final String? Function(String?)? validator;

  const GymFormField({

    super.key,

    required this.controller,

    required this.hint,

    required this.icon,

    this.validator,

    this.obscure=false,

  });

  @override
  Widget build(BuildContext context) {

    return TextFormField(

      controller: controller,

      obscureText: obscure,

      validator: validator,

      style: const TextStyle(
        color: AppColors.textPrimary,
      ),

      decoration: InputDecoration(

        hintText: hint,

        prefixIcon: Icon(
          icon,
          color: AppColors.primary,
        ),

        filled: true,

        fillColor: AppColors.surface,

        border: OutlineInputBorder(

          borderRadius:
          BorderRadius.circular(
              AppRadius.lg),

          borderSide: BorderSide.none,

        ),
      ),
    );
  }
}