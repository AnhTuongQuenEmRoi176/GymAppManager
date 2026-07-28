import '../core/utils/validators.dart';
import 'auth_controller.dart';

class LoginController {

  final AuthController _auth = AuthController();

  String? validateEmail(String value){
    return Validators.email(value);
  }

  String? validatePassword(String value){
    return Validators.password(value);
  }

  Future<bool> login(
      String email,
      String password,
      ) async{

    return await _auth.login(
      email,
      password,
    );

  }

}