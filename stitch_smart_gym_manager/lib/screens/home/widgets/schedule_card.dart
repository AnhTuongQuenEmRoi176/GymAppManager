import 'package:flutter/material.dart';

import '../../../widgets/cards/gym_card.dart';

class ScheduleCard extends StatelessWidget {

  const ScheduleCard({super.key});

  @override
  Widget build(BuildContext context) {

    return const GymCard(

      child: Column(

        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Text("Lịch tập hôm nay"),

          SizedBox(height: 10),

          Text(
            "18:00 - Ngực + Vai",
          ),

        ],

      ),

    );

  }

}