import 'package:flutter/material.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Đăng ký"),
      ),
      body: const Center(
        child: Text(
          "Chức năng đăng ký sẽ được phát triển sau.",
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  }
}