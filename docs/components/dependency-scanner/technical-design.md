# Dependency Scanner - Technical Design

## Genel Yaklaşım

Dependency Scanner, Python projelerinde kullanılan paketleri ve sürümlerini analiz ederek bilinen güvenlik açıklarını tespit edecektir.

İlk aşamada `requirements.txt` dosyası desteklenecektir. Dosyadan alınan paket ve sürüm bilgileri gerçek güvenlik açığı verileriyle karşılaştırılacaktır.

## Analiz Akışı

Bileşenin temel çalışma sırası aşağıdaki şekilde olacaktır:

1. Kullanıcıdan `requirements.txt` dosyasının yolu alınır.
2. Dosyanın varlığı kontrol edilir.
3. Dosya UTF-8 formatında okunur.
4. Boş satırlar ve yorum satırları atlanır.
5. Paket adı, sürüm operatörü ve sürüm bilgisi ayrıştırılır.
6. Paket adı standart hâle getirilir.
7. Paket ve sürüm bilgisi güvenlik açığı servisine gönderilir.
8. Servisten gelen advisory kayıtları incelenir.
9. Kullanılan sürümü etkileyen kayıtlar bulguya dönüştürülür.
10. Sonuçlar terminalde gösterilir.
11. İstenirse sonuçlar JSON dosyasına yazılır.

## Requirements Ayrıştırma

İlk sürümde öncelikle sabit sürüm belirten satırlar desteklenecektir.

Örnek:

```text
Flask==2.0.0
requests==2.25.0
```

Bu satırlardan aşağıdaki bilgiler alınacaktır:

* Paket adı
* Sürüm operatörü
* Kullanılan sürüm

Örnek ayrıştırılmış veri:

```json
{
  "package": "Flask",
  "operator": "==",
  "version": "2.0.0"
}
```

Boş satırlar ve `#` karakteriyle başlayan yorum satırları analiz dışında bırakılacaktır.

## Paket Adı Normalizasyonu

Paket adları karşılaştırılmadan önce standart hâle getirilecektir.

Örneğin aşağıdaki yazımlar aynı paketi ifade edebilir:

```text
sample-package
sample_package
Sample-Package
```

Normalizasyon sırasında:

* Harfler küçük harfe çevrilecektir.
* Tire ve alt çizgi gibi ayırıcılar ortak bir biçime dönüştürülecektir.

## Güvenlik Açığı Kaynağı

Gerçek güvenlik açığı verileri için OSV API kullanılması planlanmaktadır.

API sorgusunda temel olarak şu bilgiler kullanılacaktır:

* Paket ekosistemi
* Paket adı
* Paket sürümü

Python paketleri için ekosistem değeri PyPI olacaktır.

## API Yanıtının İşlenmesi

API yanıtında güvenlik açığı bulunduğunda aşağıdaki bilgiler alınmaya çalışılacaktır:

* Advisory kimliği
* CVE kimliği
* Güvenlik açığı açıklaması
* Etkilenen sürüm aralığı
* Düzeltilmiş sürüm
* Kaynak bağlantısı

Her kayıtta bütün alanlar bulunmayabilir. Eksik alanlar programın hata vermesine neden olmamalıdır.

## Bulgu Yapısı

Her bulgu aşağıdaki bilgileri içerecektir:

* Paket adı
* Kullanılan sürüm
* Advisory veya CVE kimliği
* Önem seviyesi
* Açıklama
* Düzeltilmiş sürüm
* Kaynak

Örnek bir bulgu:

```json
{
  "package": "example-package",
  "installed_version": "1.0.0",
  "advisory_id": "OSV-EXAMPLE",
  "severity": "high",
  "message": "Kullanılan sürüm bilinen bir güvenlik açığından etkileniyor.",
  "fixed_version": "1.0.1"
}
```

## Hata Yönetimi

Aşağıdaki durumlar kontrollü şekilde yönetilecektir:

* Dosyanın bulunamaması
* Dosyanın okunamaması
* Satırın ayrıştırılamaması
* Sürüm bilgisinin bulunmaması
* İnternet bağlantısının olmaması
* API isteğinin zaman aşımına uğraması
* API servisinden geçersiz yanıt alınması

Bir pakette hata oluşması durumunda mümkünse diğer paketlerin analizi devam edecektir.

## Test Yaklaşımı

Unit testlerde doğrudan canlı API kullanılmayacaktır.

Testlerin internet bağlantısından ve API değişikliklerinden etkilenmemesi için gerçek advisory kayıtlarından hazırlanmış yerel fixture verileri kullanılacaktır.

Canlı API bağlantısı ayrıca entegrasyon testiyle kontrol edilecektir.

## Gelecek Geliştirmeler

* Farklı sürüm operatörlerinin desteklenmesi
* Birden fazla requirements dosyasının taranması
* `pyproject.toml` desteği
* API zaman aşımı ve tekrar deneme yönetimi
* Yerel önbellek kullanımı
* Terminal ve JSON raporları
* Unit ve entegrasyon testleri

## Navigation

- [Dependency Scanner sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)