import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../config/app_config.dart';
import '../storage/token_storage.dart';
import 'api_exception.dart';

class ApiClient {
  ApiClient({required TokenStorage tokenStorage})
      : _tokenStorage = tokenStorage,
        dio = Dio(
          BaseOptions(
            baseUrl: AppConfig.apiBaseUrl,
            connectTimeout: AppConfig.connectTimeout,
            receiveTimeout: AppConfig.receiveTimeout,
            sendTimeout: AppConfig.connectTimeout,
            headers: const {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        ) {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _tokenStorage.readAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          if (kDebugMode) {
            debugPrint('[API] --> ${options.method} ${options.uri}');
            if (options.data != null) {
              final safeData = options.data is Map
                  ? Map<Object?, Object?>.from(options.data as Map)
                  : options.data;
              if (safeData is Map) {
                for (final key in const [
                  'password',
                  'current_password',
                  'new_password',
                  'confirm_password',
                  'refresh_token',
                ]) {
                  if (safeData.containsKey(key)) safeData[key] = '******';
                }
              }
              debugPrint('[API] request: $safeData');
            }
          }
          handler.next(options);
        },
        onResponse: (response, handler) {
          if (kDebugMode) {
            debugPrint(
              '[API] <-- ${response.statusCode} '
              '${response.requestOptions.method} ${response.requestOptions.uri}',
            );
            debugPrint('[API] response: ${response.data}');
          }
          handler.next(response);
        },
        onError: (error, handler) {
          if (kDebugMode) {
            debugPrint(
              '[API] xx ${error.response?.statusCode ?? '-'} '
              '${error.requestOptions.method} ${error.requestOptions.uri}',
            );
            debugPrint('[API] DioExceptionType: ${error.type}');
            debugPrint('[API] error: ${error.message}');
            debugPrint('[API] response: ${error.response?.data}');
          }
          handler.next(error);
        },
      ),
    );
  }

  final Dio dio;
  final TokenStorage _tokenStorage;

  Future<Map<String, dynamic>> getJson(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await dio.get<dynamic>(
        path,
        queryParameters: queryParameters,
      );
      return _asJsonMap(response.data);
    } on DioException catch (error) {
      throw _mapError(error);
    }
  }

  Future<List<dynamic>> getList(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await dio.get<dynamic>(
        path,
        queryParameters: queryParameters,
      );
      final data = response.data;
      if (data is List) return List<dynamic>.from(data);
      throw const ApiException('Phản hồi API không đúng định dạng danh sách.');
    } on DioException catch (error) {
      throw _mapError(error);
    }
  }

  Future<Map<String, dynamic>> postJson(
    String path, {
    Object? data,
  }) async {
    try {
      final response = await dio.post<dynamic>(path, data: data);
      return _asJsonMap(response.data);
    } on DioException catch (error) {
      throw _mapError(error);
    }
  }

  Future<Map<String, dynamic>> patchJson(
    String path, {
    Object? data,
  }) async {
    try {
      final response = await dio.patch<dynamic>(path, data: data);
      return _asJsonMap(response.data);
    } on DioException catch (error) {
      throw _mapError(error);
    }
  }

  Map<String, dynamic> _asJsonMap(dynamic data) {
    if (data == null) return <String, dynamic>{};
    if (data is Map<String, dynamic>) return data;
    if (data is Map) return data.cast<String, dynamic>();
    throw const ApiException('Phản hồi API không đúng định dạng JSON object.');
  }

  ApiException _mapError(DioException error) {
    final response = error.response;
    final statusCode = response?.statusCode;
    final serverMessage = _extractServerMessage(response?.data);

    if (serverMessage != null && serverMessage.isNotEmpty) {
      return ApiException(serverMessage, statusCode: statusCode);
    }

    final message = switch (error.type) {
      DioExceptionType.connectionTimeout =>
        'Kết nối máy chủ quá thời gian. Vui lòng kiểm tra mạng và thử lại.',
      DioExceptionType.sendTimeout =>
        'Gửi dữ liệu đến API quá thời gian. Vui lòng thử lại.',
      DioExceptionType.receiveTimeout =>
        'API phản hồi quá chậm. Vui lòng thử lại.',
      DioExceptionType.transformTimeout =>
        'Quá thời gian xử lý dữ liệu phản hồi từ API.',
      DioExceptionType.connectionError =>
        'Không kết nối được máy chủ. Vui lòng kiểm tra backend và kết nối mạng.',
      DioExceptionType.badCertificate =>
        'Chứng chỉ kết nối API không hợp lệ.',
      DioExceptionType.cancel => 'Yêu cầu đã bị hủy.',
      DioExceptionType.badResponse =>
        'API trả về lỗi HTTP ${statusCode ?? 'không xác định'}.',
      DioExceptionType.unknown =>
        'Lỗi kết nối API: ${error.message ?? 'không xác định'}.',
    };

    return ApiException(message, statusCode: statusCode);
  }

  String? _extractServerMessage(dynamic data) {
    if (data is Map) {
      final message = data['message'];
      if (message != null) return message.toString();

      final detail = data['detail'];
      if (detail is String) return detail;
      if (detail is List && detail.isNotEmpty) {
        final first = detail.first;
        if (first is Map && first['msg'] != null) {
          return first['msg'].toString();
        }
        return first.toString();
      }
      if (detail != null) return detail.toString();
    }
    return null;
  }
}
