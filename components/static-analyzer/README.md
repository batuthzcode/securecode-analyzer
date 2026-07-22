# Static Code Analyzer

## Amaç

Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit etmek.

## Planlanan Kontroller

* Uzun fonksiyon tespiti
* Boş `except` bloğu tespiti
* `TODO` ve `FIXME` ifadelerinin tespiti
* Fonksiyon ve sınıf isimlendirme kontrolü
* Kod içine yazılmış parola, token veya anahtar tespiti

## Kullanılacak Yöntemler

* Python kodunun yapısal analizi için `ast` modülü
* Metin tabanlı kontroller için regex ve satır taraması

## Girdi

* Tek bir Python dosyası
* Python proje klasörü

## Çıktı

Her bulgu için aşağıdaki bilgiler üretilecektir:

* Dosya yolu
* Satır numarası
* Kural adı
* Önem seviyesi
* Bulgu açıklaması
* Çözüm önerisi

Sonuçlar terminal ve JSON formatında sunulacaktır.

## Documentation

- [Analiz ve Gereksinimler](docs/analysis.md)
- [Teknik Tasarım](docs/technical-design.md)


## Mevcut Durum

AST kullanarak fonksiyonları bulan ve belirlenen satır sınırından uzun fonksiyonları raporlayan ilk prototip hazırlanmıştır.
## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../README.md)