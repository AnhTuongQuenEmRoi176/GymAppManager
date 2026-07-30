import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_message_banner.dart';
import '../providers/auth_provider.dart';

class ForgotPasswordPage extends ConsumerStatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  ConsumerState<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends ConsumerState<ForgotPasswordPage> {
  final _accountFormKey = GlobalKey<FormState>();
  final _resetFormKey = GlobalKey<FormState>();
  final _accountController = TextEditingController();
  final _otpController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _otpRequested = false;
  bool _loading = false;
  bool _obscureNew = true;
  bool _obscureConfirm = true;
  String? _message;
  String? _error;
  String? _debugOtp;

  @override
  void dispose() {
    _accountController.dispose();
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    FocusScope.of(context).unfocus();
    if (!(_accountFormKey.currentState?.validate() ?? false)) return;

    setState(() {
      _loading = true;
      _error = null;
      _message = null;
    });
    try {
      final result = await ref
          .read(authControllerProvider.notifier)
          .requestPasswordReset(_accountController.text.trim());
      if (!mounted) return;
      setState(() {
        _loading = false;
        _otpRequested = true;
        _message = result.message;
        _debugOtp = result.debugOtp;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  Future<void> _resetPassword() async {
    FocusScope.of(context).unfocus();
    if (!(_resetFormKey.currentState?.validate() ?? false)) return;

    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await ref.read(authControllerProvider.notifier).resetPassword(
            account: _accountController.text.trim(),
            otp: _otpController.text.trim(),
            newPassword: _newPasswordController.text,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Đặt lại mật khẩu thành công.')),
      );
      Navigator.of(context).pop();
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Quên mật khẩu')),
      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.primarySoft,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.lock_reset_rounded,
                  color: AppColors.primary,
                  size: 28,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                _otpRequested ? 'Tạo mật khẩu mới' : 'Xác minh tài khoản',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 6),
              Text(
                _otpRequested
                    ? 'Nhập mã OTP và mật khẩu mới. Mật khẩu xác nhận phải trùng khớp.'
                    : 'Nhập số điện thoại hoặc email đã đăng ký để nhận mã OTP.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 22),
              if (!_otpRequested) _buildAccountForm() else _buildResetForm(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAccountForm() {
    return Form(
      key: _accountFormKey,
      child: Column(
        children: [
          TextFormField(
            controller: _accountController,
            autocorrect: false,
            autofillHints: const <String>[],
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) {
              if (!_loading) _requestOtp();
            },
            decoration: const InputDecoration(
              labelText: 'Số điện thoại hoặc email',
              hintText: 'Nhập thông tin tài khoản',
              prefixIcon: Icon(Icons.person_search_outlined),
            ),
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Vui lòng nhập thông tin tài khoản.';
              }
              if (value.trim().length < 3) {
                return 'Thông tin tài khoản chưa hợp lệ.';
              }
              return null;
            },
          ),
          if (_error != null) ...[
            const SizedBox(height: 14),
            AppMessageBanner(message: _error!, type: AppMessageType.error),
          ],
          const SizedBox(height: 18),
          FilledButton(
            onPressed: _loading ? null : _requestOtp,
            child: _loading
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.2, color: Colors.white),
                  )
                : const Text('Gửi mã OTP'),
          ),
        ],
      ),
    );
  }

  Widget _buildResetForm() {
    return Form(
      key: _resetFormKey,
      child: Column(
        children: [
          if (_message != null) ...[
            AppMessageBanner(
              title: 'Đã gửi yêu cầu',
              message: _debugOtp == null
                  ? _message!
                  : '${_message!}\nOTP kiểm thử: $_debugOtp',
              type: AppMessageType.success,
            ),
            const SizedBox(height: 16),
          ],
          TextFormField(
            controller: _otpController,
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.next,
            maxLength: 6,
            decoration: const InputDecoration(
              labelText: 'Mã OTP',
              hintText: 'Nhập 6 chữ số',
              prefixIcon: Icon(Icons.password_rounded),
              counterText: '',
            ),
            validator: (value) {
              if (value == null || value.trim().length != 6) {
                return 'Mã OTP phải gồm 6 chữ số.';
              }
              return null;
            },
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _newPasswordController,
            obscureText: _obscureNew,
            autocorrect: false,
            enableSuggestions: false,
            textInputAction: TextInputAction.next,
            decoration: InputDecoration(
              labelText: 'Mật khẩu mới',
              hintText: 'Ít nhất 6 ký tự',
              prefixIcon: const Icon(Icons.lock_outline_rounded),
              suffixIcon: IconButton(
                onPressed: () => setState(() => _obscureNew = !_obscureNew),
                icon: Icon(
                  _obscureNew ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                ),
              ),
            ),
            validator: (value) {
              if (value == null || value.length < 6) {
                return 'Mật khẩu mới phải có ít nhất 6 ký tự.';
              }
              return null;
            },
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _confirmPasswordController,
            obscureText: _obscureConfirm,
            autocorrect: false,
            enableSuggestions: false,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) {
              if (!_loading) _resetPassword();
            },
            decoration: InputDecoration(
              labelText: 'Nhập lại mật khẩu mới',
              hintText: 'Nhập lại để xác nhận',
              prefixIcon: const Icon(Icons.verified_user_outlined),
              suffixIcon: IconButton(
                onPressed: () => setState(
                  () => _obscureConfirm = !_obscureConfirm,
                ),
                icon: Icon(
                  _obscureConfirm
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                ),
              ),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Vui lòng nhập lại mật khẩu mới.';
              }
              if (value != _newPasswordController.text) {
                return 'Hai mật khẩu mới không trùng khớp.';
              }
              return null;
            },
          ),
          if (_error != null) ...[
            const SizedBox(height: 14),
            AppMessageBanner(message: _error!, type: AppMessageType.error),
          ],
          const SizedBox(height: 18),
          FilledButton(
            onPressed: _loading ? null : _resetPassword,
            child: _loading
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.2, color: Colors.white),
                  )
                : const Text('Cập nhật mật khẩu'),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: _loading
                ? null
                : () => setState(() {
                      _otpRequested = false;
                      _message = null;
                      _error = null;
                      _debugOtp = null;
                    }),
            child: const Text('Dùng tài khoản khác'),
          ),
        ],
      ),
    );
  }
}
