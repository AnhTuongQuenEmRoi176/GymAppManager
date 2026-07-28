import 'package:flutter/material.dart';

import '../home/home_screen.dart';
import '../profile/profile_screen.dart';
import '../qr/qr_screen.dart';
import '../schedule/schedule_screen.dart';
import '../../widgets/navigation/gym_bottom_navigation.dart';

class BottomNavigationScreen extends StatefulWidget {
  const BottomNavigationScreen({super.key});

  @override
  State<BottomNavigationScreen> createState() =>
      _BottomNavigationScreenState();
}

class _BottomNavigationScreenState
    extends State<BottomNavigationScreen> {

  int currentIndex = 0;

  final pages = const [

    HomeScreen(),

    ScheduleScreen(),

    QrScreen(),

    ProfileScreen(),

  ];

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: pages[currentIndex],

      bottomNavigationBar: GymBottomNavigation(

        currentIndex: currentIndex,

        onTap: (index){

          setState(() {

            currentIndex=index;

          });

        },

      ),

    );

  }

}