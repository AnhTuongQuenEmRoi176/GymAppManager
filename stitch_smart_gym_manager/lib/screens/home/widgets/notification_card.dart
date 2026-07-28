import 'package:flutter/material.dart';

import '../../../widgets/cards/gym_card.dart';

class NotificationCard extends StatelessWidget {

  const NotificationCard({super.key});

  @override
  Widget build(BuildContext context) {

    return const GymCard(

      child: Column(

        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Text(
            "Thông báo",
          ),

          SizedBox(height: 10),

          Text(
            "• Gia hạn gói tập",
          ),

          Text(
            "• PT hôm nay",
          ),

        ],

      ),

    );

  }

}