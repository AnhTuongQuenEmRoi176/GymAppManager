import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_text_styles.dart';

import '../../../widgets/buttons/primary_button.dart';
import '../../../widgets/cards/gym_card.dart';
import '../../../widgets/inputs/gym_text_field.dart';

class ModernLoginScreen extends StatefulWidget {
  const ModernLoginScreen({super.key});

  @override
  State<ModernLoginScreen> createState() =>
      _ModernLoginScreenState();
}

class _ModernLoginScreenState
    extends State<ModernLoginScreen> {

  final emailController = TextEditingController();

  final passwordController =
      TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,

      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(
              AppSpacing.md),

          child: SizedBox(
            width: 420,

            child: GymCard(
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.stretch,

                children: [

                  const Icon(
                    Icons.fitness_center,
                    size: 70,
                    color: AppColors.primary,
                  ),

                  const SizedBox(height: 20),

                  Text(
                    "GYM MASTER",
                    textAlign: TextAlign.center,
                    style: AppTextStyles.headlineLarge,
                  ),

                  const SizedBox(height: 10),

                  Text(
                    "Chào mừng trở lại",
                    textAlign: TextAlign.center,
                    style:
                        AppTextStyles.bodyMedium,
                  ),

                  const SizedBox(height: 35),

                  GymTextField(
                    hint: "Email",

                    icon: Icons.email,

                    controller:
                        emailController,
                  ),

                  const SizedBox(height: 20),

                  GymTextField(
                    hint: "Mật khẩu",

                    icon: Icons.lock,

                    obscure: true,

                    controller:
                        passwordController,
                  ),

                  const SizedBox(height: 30),

                  PrimaryButton(
                    text: "ĐĂNG NHẬP",

                    icon: Icons.login,

                    onPressed: () {},
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}