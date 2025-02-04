import 'dart:typed_data';
import 'package:final_odev/service/api-service.dart';
import 'package:flutter/material.dart';
class ApiProvider with ChangeNotifier {
  final ApiService _apiService;

  ApiProvider(String baseUrl) : _apiService = ApiService(baseUrl);

  String? result;
  String? errorMessage;
  bool isLoading = false;

  Future<void> uploadFile(String filePath) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      result = await _apiService.uploadFile(filePath);
    } catch (e) {
      errorMessage = 'Hata: $e';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> uploadFileBytes(Uint8List fileBytes, String fileName) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      result = await _apiService.uploadFileBytes(fileBytes, fileName);
    } catch (e) {
      errorMessage = 'Hata: $e';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }  
}