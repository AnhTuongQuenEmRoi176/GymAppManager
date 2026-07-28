import 'package:flutter/material.dart';

import '../../../widgets/buttons/primary_button.dart';
import '../../../widgets/cards/gym_card.dart';

class QrCard extends StatelessWidget {

  const QrCard({super.key});

  @override
  Widget build(BuildContext context) {

    return GymCard(

      child: Column(

        children: [

          const Icon(
            Icons.qr_code_2,
            size: 80,
          ),

          const SizedBox(height: 20),

          PrimaryButton(

            text: "Quét QR",

            onPressed: (){},

          ),

        ],

      ),

    );

  }

}