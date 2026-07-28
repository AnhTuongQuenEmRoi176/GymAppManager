import '../repositories/auth_repository.dart';

class AuthController {
  final AuthRepository _repository = AuthRepository();

  Future<bool> login(
    String email,
    String password,
  ) async {
    return _repository.login(email, password);
  }
}