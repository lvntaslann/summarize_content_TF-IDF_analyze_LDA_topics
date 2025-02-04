# Yapay Zeka Destekli İçerik Özetleme ve Analiz Uygulaması

## Giriş

Bu proje, Google Scholar, Medium, TÜBİTAK, YouTube gibi platformlarda paylaşılan içeriklerin özet bilgilerini çıkarmak ve bu içeriklerde anlatılanların *TF-IDF* ve *LDA* yöntemleriyle oluşturulan kelime bulutlarıyla ilişkisini incelemek amacıyla geliştirilmiştir. Uygulama, içeriklerde aktarılan bilgilerin doğru bir şekilde iletilip iletilmediğini test etmek için kullanılacaktır.

PDF, Excel ve Word gibi dosya türlerinde yer alan bir veya birden fazla bağlantı üzerinden erişilen içeriklerin özetleri, *TF-IDF* ve *LDA* kelime bulutu çıktılarıyla birlikte kullanıcıya sunulur. Bu sayede, içeriklerin öz ve analiz tabanlı görsel çıktıları karşılaştırılarak kullanıcıya zenginleştirilmiş bir bilgi aktarımı sağlanır.

---

## Proje Görseli

![Proje Görseli](https://github.com/lvntaslann/summarize_content_TF-IDF_analyze_LDA_topics/blob/main/images/images.png)
---

## Kullanılan Yazılımlar

### OpenRouter
- *Açıklama*: [OpenRouter](https://openrouter.ai/) sitesi üzerinden Google: LearnLM 1.5 Pro Experimental (free) modeli için API key oluşturuldu.
- *Kullanım Amacı*: Yapay zeka modeliyle etkileşim kurmak ve içerik özetleme işlemlerini gerçekleştirmek.

### FastAPI
- *Açıklama*: Mistral 7B modeli için request işlemlerinde bulunmak amacıyla FastAPI tercih edildi.
- *Kullanılan Kütüphaneler*:
  - pip install fastapi: Modern ve hızlı web uygulamaları geliştirmek için bir framework.
  - pip install uvicorn: FastAPI uygulamalarını çalıştırmak için kullanılan bir ASGI sunucusu.
  - pip install pandas: Veri analizi ve manipülasyonu için güçlü bir araç.
  - pip install matplotlib: Grafik ve veri görselleştirme için popüler bir kütüphane.
  - pip install wordcloud: Kelime bulutları oluşturmak için kullanılan bir araç.
  - pip install scikit-learn: Makine öğrenimi algoritmaları ve veri işleme araçları sunar.
  - pip install gensim: Doğal dil işleme ve konu modelleme için kullanılan güçlü bir kütüphane.
  - pip install youtube-transcript-api: YouTube videolarından altyazı/transkript almak için bir API.
  - pip install beautifulsoup4: HTML ve XML belgelerini ayrıştırmak ve veri çıkarmak için kullanılır.
  - pip install requests: HTTP istekleri yapmak için kullanılan popüler bir kütüphane.
  - pip install nltk: Doğal dil işleme (NLP) için araçlar sunan bir kütüphane.
  - pip install fpdf: PDF belgeleri oluşturmak için kullanılan bir kütüphane.
  - pip install PyPDF2: PDF dosyalarını okumak ve işlemek için kullanılan bir araç.


### Flutter
- *Açıklama*: Uygulamanın arayüzü Flutter ile geliştirildi.
- *Kurulum*: Flutter SDK kurulumu [bu adresten](https://docs.flutter.dev/get-started/install) yapılabilir.
- *Kullanılan Kütüphaneler*:
  - http: ^1.2.2: HTTP istekleri göndermek için gerekli kütüphane.
  - lottie: ^3.1.3: Lottie animasyonlarının Flutter üzerinde çalışmasını sağlar.
  - provider: ^6.1.2: State management yapılmasını sağlar.

---

## Proje Yapısı

1. *Arayüz ve backend iletişimi
    - FastAPI ile arayüz üzerinden kullanıcı tarafından yüklenen dosya ile işlemler yapılır

3. *İçerik Özetleme*:
   - Belirtilen platformlardan içerikler çekilir.
   - Yapay zeka modeli kullanılarak içerikler özetlenir.

4. *Kelime Bulutu Oluşturma*:
   - *TF-IDF* ve *LDA* yöntemleri kullanılarak kelime bulutları oluşturulur.
   - Bu bulutlar, içeriklerin anahtar kelimelerini görselleştirir.

---


### Gereksinimler
- Python 3.10
- Flutter SDK
- FastAPI
