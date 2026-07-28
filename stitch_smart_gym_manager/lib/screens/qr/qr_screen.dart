import 'package:flutter/material.dart';

class QrScreen extends StatelessWidget {

  const QrScreen({super.key});

  @override
  Widget build(BuildContext context) {

    return const Scaffold(

      body: Center(

        child: Text(

          "QR",

          style: TextStyle(

            fontSize: 40,

          ),

        ),

      ),

    );

  }

}