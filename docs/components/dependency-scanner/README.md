# Dependency and CVE Scanner

## Amaç

Python projelerinde kullanılan bağımlılıkların sürümlerini inceleyerek bilinen güvenlik açıklarını tespit etmek.

## Planlanan İşlemler

* `requirements.txt` dosyasını okuma
* Paket adlarını ve sürüm bilgilerini ayırma
* Paket adlarını standart hâle getirme
* Paketleri gerçek güvenlik açığı verileriyle karşılaştırma
* Etkilenen sürümleri tespit etme
* Güvenli sürüm önerisi sunma

## Kullanılacak Yöntemler

* Bağımlılık bilgilerini okumak için Python dosya işlemleri
* Güvenlik açığı sorgulamak için OSV API
* Testlerde kullanılmak üzere yerel örnek güvenlik açığı verileri

## Girdi

* `requirements.txt` dosyası

## Çıktı

Her güvenlik açığı için aşağıdaki bilgiler üretilecektir:

* Paket adı
* Kullanılan sürüm
* CVE veya advisory kimliği
* Güvenlik açığı açıklaması
* Önem seviyesi
* Güvenli veya düzeltilmiş sürüm önerisi

Sonuçlar terminal ve JSON formatında sunulacaktır.

## Documentation

- [Analiz ve Gereksinimler](analysis.md)
- [Teknik Tasarım](technical-design.md)

## Mevcut Durum

Bu bileşen şu anda analiz ve teknik tasarım aşamasındadır. Geliştirme işlemi proje planındaki ilgili haftada yapılacaktır.
## Navigation

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
