# Dependency Scanner - Analysis

## Amaç

Bu bileşenin amacı, Python projelerinde kullanılan bağımlılıkları inceleyerek bilinen güvenlik açıklarını tespit etmektir.

## Girdi

Bileşen ilk aşamada aşağıdaki dosyayı girdi olarak kabul edecektir:

* `requirements.txt`

Dosyada paket adıyla birlikte sürüm bilgisinin bulunması beklenmektedir.

Örnek:

```text
Flask==2.0.0
requests==2.25.0
```

## Planlanan İşlemler

### Requirements Dosyasını Okuma

`requirements.txt` dosyası satır satır okunacaktır.

Boş satırlar ve yorum satırları analiz dışında bırakılacaktır.

### Paket Bilgilerini Ayırma

Her satırdan aşağıdaki bilgiler alınacaktır:

* Paket adı
* Kullanılan sürüm
* Sürüm karşılaştırma operatörü

İlk sürümde öncelikle `==` ile sabitlenmiş paketler desteklenecektir.

### Paket Adını Standartlaştırma

Paket adları güvenlik açığı kaynağıyla karşılaştırılmadan önce standart hâle getirilecektir.

Büyük-küçük harf farkları ve paket adındaki bazı ayırıcı karakterler dikkate alınacaktır.

### Güvenlik Açığı Sorgulama

Paket ve sürüm bilgisi OSV gibi gerçek bir güvenlik açığı kaynağında sorgulanacaktır.

Paketin kullanılan sürümünü etkileyen bir advisory veya CVE bulunursa bulgu oluşturulacaktır.

### Güvenli Sürüm Bilgisi

Güvenlik açığı kaydında düzeltilmiş sürüm bilgisi bulunuyorsa kullanıcıya gösterilecektir.

Her güvenlik açığında güvenli sürüm bilgisi bulunmayabileceği için bu alan zorunlu olmayacaktır.

## Çıktı

Her bulgu için aşağıdaki bilgiler üretilecektir:

* Paket adı
* Kullanılan sürüm
* Advisory veya CVE kimliği
* Güvenlik açığı açıklaması
* Önem seviyesi
* Düzeltilmiş sürüm bilgisi
* Güvenlik açığı kaynağı

Sonuçlar terminalde gösterilecek ve JSON formatında kaydedilebilecektir.

## Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır hata mesajlarıyla bildirilecektir:

* `requirements.txt` dosyasının bulunamaması
* Dosyanın okunamaması
* Paket satırının ayrıştırılamaması
* Paket sürüm bilgisinin eksik olması
* Güvenlik açığı servisine ulaşılamaması
* Servisten geçersiz cevap alınması

Bir paket sorgulanamazsa mümkün olduğu durumda diğer paketlerin analizine devam edilecektir.

## Test Yaklaşımı

Unit testlerin internet bağlantısına bağlı olmaması için gerçek güvenlik açığı kayıtlarından hazırlanmış yerel örnek veriler kullanılacaktır.

Canlı kullanım sırasında ise güncel güvenlik açığı bilgileri API üzerinden alınacaktır.

## Mevcut Durum

Bu bileşen şu anda analiz ve teknik tasarım aşamasındadır.

Kod geliştirme aşamasında önce `requirements.txt` dosyasının ayrıştırılması, daha sonra güvenlik açığı sorgulama işlemi geliştirilecektir.

## Navigation

- [Dependency Scanner sayfasına dön](../README.md)
- [Tüm bileşenlere dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
