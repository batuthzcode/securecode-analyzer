# Static Code Analyzer - Analysis

## Amaç

Bu bileşenin amacı, Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit etmektir.

## Girdi

Bileşen aşağıdaki girdileri kabul edecektir:

* Tek bir Python dosyası
* Bir Python proje klasörü

## Planlanan Kontroller

### Uzun Fonksiyon Kontrolü

Fonksiyonların başlangıç ve bitiş satırları hesaplanacaktır. Belirlenen satır sınırını aşan fonksiyonlar raporlanacaktır.

Bu kontrol için Python `ast` modülü kullanılacaktır.

### Boş Except Kontrolü

İçerisinde yalnızca `pass` bulunan veya hata üzerinde işlem yapmayan `except` blokları tespit edilecektir.

### TODO ve FIXME Kontrolü

Kaynak kod içerisindeki `TODO` ve `FIXME` ifadeleri satır taramasıyla bulunacaktır.

### İsimlendirme Kontrolü

Fonksiyon ve sınıf isimlerinin belirlenen Python isimlendirme kurallarına uygun olup olmadığı kontrol edilecektir.

### Hardcoded Secret Kontrolü

Kod içerisinde doğrudan yazılmış parola, token veya API anahtarı olabilecek ifadeler aranacaktır.

Bu kontrol kesin bir güvenlik açığı kararı vermek yerine şüpheli durumları raporlayacaktır.

## Çıktı

Her bulgu için aşağıdaki bilgiler üretilecektir:

* Dosya yolu
* Satır numarası
* Kural adı
* Önem seviyesi
* Bulgu açıklaması
* Çözüm önerisi

Sonuçlar terminalde gösterilecek ve JSON formatında kaydedilebilecektir.

## Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır bir hata mesajıyla bildirilecektir:

* Dosyanın bulunamaması
* Dosyanın okunamaması
* Python sözdizimi hatası bulunması
* Geçersiz dosya veya klasör yolu verilmesi

## Mevcut Durum

AST kullanılarak fonksiyonları bulan ve belirlenen satır sınırını aşan fonksiyonları raporlayan ilk prototip hazırlanmıştır.

Prototip şu anda tek bir örnek Python dosyası üzerinde çalışmaktadır.

## Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)