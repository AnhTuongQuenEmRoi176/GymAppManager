import 'package:flutter/material.dart';
import 'package:gym_mobile/screens/navigation/bottom_navigation_screen.dart';
import '../../screens/home/home_screen.dart';
import 'app_routes.dart';

class AppRouter {
  AppRouter._();

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.home:
        return MaterialPageRoute(
          builder: (_) => const HomeScreen(),
        );

      case AppRoutes.login:
      default:
        return MaterialPageRoute(
          builder: (_) => const BottomNavigationScreen(),
        );
    }
  }
}