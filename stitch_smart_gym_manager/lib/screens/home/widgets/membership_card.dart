import 'package:flutter/material.dart';

import '../../../widgets/cards/gym_card.dart';

class MembershipCard extends StatelessWidget {
  const MembershipCard({super.key});

  @override
  Widget build(BuildContext context) {

    return GymCard(

      child: Column(

        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: const [

          Text(
            "Gói tập",
          ),

          SizedBox(height: 10),

          Text(
            "Premium",
          ),

          SizedBox(height: 5),

          Text(
            "Còn 30 ngày",
          ),

        ],

      ),

    );

  }
}