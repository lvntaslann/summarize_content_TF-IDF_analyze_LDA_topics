import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import 'package:lottie/lottie.dart';
import '../provider/api-provider.dart';


class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    final apiProvider = Provider.of<ApiProvider>(context);

    return Scaffold(
      backgroundColor: Color.fromARGB(255, 3, 76, 39).withOpacity(0.9),
      body: Column(
        children: [
          MyNavBar(),
          SizedBox(height: 80),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Column(
                children: [
                  LottieBuilder.asset(
                    "assets/lottie-anim.json",
                    width: 350,
                    height: 275,
                  ),
                  Text(
                    "Web sitesi\nözetle",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xffDFDFDF),
                      fontSize: 35,
                      letterSpacing: 5,
                      wordSpacing: 1,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              SizedBox(width: 75),
              Container(
                height: size.height * 0.4,
                width: size.width * 0.30,
                decoration: BoxDecoration(
                  color: Color(0xffD9C3C3),
                  borderRadius: BorderRadius.circular(50),
                  border: Border.all(
                    color: Colors.black,
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.5),
                      spreadRadius: 2,
                      blurRadius: 5,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      "Excel, PDF\nWord...",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 45,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 20),
                    if (apiProvider.isLoading) CircularProgressIndicator(),
                    if (!apiProvider.isLoading && apiProvider.result != null)
                      Text(
                        apiProvider.result!,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.black,
                          fontSize: 16,
                        ),
                      ),
                    if (apiProvider.errorMessage != null)
                      Text(
                        apiProvider.errorMessage!,
                        style: TextStyle(
                          color: Colors.red,
                          fontSize: 16,
                        ),
                      ),
                    SizedBox(height: 20),
                    GestureDetector(
                      onTap: () async {
                        FilePickerResult? result =
                            await FilePicker.platform.pickFiles();
                        if (result != null) {
                          String fileName = sanitizeFileName(result.files.first.name);
                          if (result.files.first.bytes != null) {
                            Uint8List fileBytes = result.files.first.bytes!;
                            await apiProvider.uploadFileBytes(fileBytes, fileName);
                          } else {
                            String filePath = result.files.first.path!;
                            await apiProvider.uploadFile(filePath);
                          }
                        }
                      },
                      child: Container(
                        height: size.height * 0.10,
                        width: size.width * 0.15,
                        decoration: BoxDecoration(
                          color: Color(0xFF2FD691),
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: Center(
                          child: Text(
                            "Dosya yükle",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 30,
                              fontWeight: FontWeight.w400,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String getFileExtension(String fileName) {
  return fileName.split('.').last.toLowerCase();
}

String sanitizeFileName(String fileName) {
  return fileName.replaceAll(RegExp(r'[^\w\.-]'), '_');
}
}

class MyNavBar extends StatelessWidget {
  const MyNavBar({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          height: size.height * 0.15,
          width: size.width,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.only(
              bottomRight: Radius.circular(50),
            ),
            color: Color(0xFF278C59).withOpacity(0.9),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              SizedBox(width: size.width * 0.15),
              Text(
                "summarizeURL",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 25,
                  fontWeight: FontWeight.w600,
                  shadows: [
                    Shadow(
                      color: Colors.grey.withOpacity(0.8),
                      offset: Offset(3, 3),
                      blurRadius: 4,
                    )
                  ],
                ),
              ),
              SizedBox(width: 400),
              Text(
                "Anasayfa",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  fontWeight: FontWeight.w300,
                ),
              ),
              SizedBox(width: 50),
              Text(
                "Anasayfa",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  fontWeight: FontWeight.w300,
                ),
              ),
              SizedBox(width: 50),
              Text(
                "Anasayfa",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  fontWeight: FontWeight.w300,
                ),
              ),
            ],
          ),
        ),
        Positioned(
          top: size.height * 0.03,
          child: Image.asset(
            "assets/gomulu-logo.jpg",
            width: size.width * 0.10,
            height: size.height * 0.15,
          ),
        ),
      ],
    );
  }
}