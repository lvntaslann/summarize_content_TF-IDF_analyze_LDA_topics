import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Future<String> uploadFile(String filePath) async {
    var request =
        http.MultipartRequest('POST', Uri.parse('$baseUrl/process-file'));
    request.files.add(await http.MultipartFile.fromPath('file', filePath));

    var response = await request.send();
    if (response.statusCode == 200) {
      final responseData = await response.stream.bytesToString();
      return responseData;
    } else {
      throw Exception('Dosya yükleme başarısız: ${response.statusCode}');
    }
  }

  Future<String> uploadFileBytes(Uint8List fileBytes, String fileName) async {
    var request =
        http.MultipartRequest('POST', Uri.parse('$baseUrl/process-file'));
    request.files.add(
      http.MultipartFile.fromBytes('file', fileBytes, filename: fileName),
    );

    var response = await request.send();
    if (response.statusCode == 200) {
      final responseData = await response.stream.bytesToString();
      return responseData;
    } else {
      throw Exception('Dosya yükleme başarısız: ${response.statusCode}');
    }
  }
}