class Validators {
  Validators._();

  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return "Không được để trống";
    }

    if (!value.contains("@")) {
      return "Email không hợp lệ";
    }

    return null;
  }

  static String? password(String? value) {
    if (value == null || value.length < 6) {
      return "Mật khẩu tối thiểu 6 ký tự";
    }

    return null;
  }
}