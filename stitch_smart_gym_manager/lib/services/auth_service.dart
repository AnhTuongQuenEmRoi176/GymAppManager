import 'api_service.dart';

class AuthService {

  Future<bool> login(

      String email,

      String password,

      ) async {

    await Future.delayed(

      const Duration(seconds: 1),

    );

    print(ApiService.baseUrl);

    return true;

  }

}