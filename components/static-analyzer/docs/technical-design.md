# Static Code Analyzer - Technical Design

## Genel Yaklaşım

Static Code Analyzer, Python kaynak kodlarını çalıştırmadan inceleyecektir.

Kodun yapısal bölümlerini incelemek için Python `ast` modülü, metin tabanlı kontroller için ise satır taraması ve regex kullanılacaktır.

## Analiz Akışı

Bileşenin temel çalışma sırası aşağıdaki şekilde olacaktır:

1. Kullanıcıdan dosya veya klasör yolu alınır.
2. Analiz edilecek Python dosyaları bulunur.
3. Dosyaların içeriği UTF-8 formatında okunur.
4. Kaynak kod `ast.parse()` ile AST yapısına dönüştürülür.
5. AST düğümleri dolaşılarak yapısal kontroller gerçekleştirilir.
6. Metin tabanlı kurallar kaynak kod satırları üzerinde çalıştırılır.
7. Bulunan problemler ortak bir bulgu yapısında saklanır.
8. Sonuçlar terminalde gösterilir.
9. İstenirse sonuçlar JSON dosyasına yazılır.

## AST Tabanlı Kontroller

AST tabanlı kontroller aşağıdaki kurallarda kullanılacaktır:

* Uzun fonksiyon tespiti
* Boş `except` bloğu tespiti
* Fonksiyon isimlendirme kontrolü
* Sınıf isimlendirme kontrolü

AST kullanılması sayesinde yorum satırları veya metin içerisindeki ifadeler gerçek Python yapılarıyla karıştırılmaz.

## Metin Tabanlı Kontroller

Satır taraması veya regex aşağıdaki kontrollerde kullanılacaktır:

* `TODO` ve `FIXME` ifadelerinin tespiti
* Parola, token veya API anahtarı olabilecek değerlerin aranması

Hardcoded secret kontrolü kesin sonuç üretmeyebilir. Bu nedenle bulunan değerler şüpheli bulgu olarak raporlanacaktır.

## Bulgu Yapısı

Her bulgu aşağıdaki bilgileri içerecektir:

* Kural kimliği
* Dosya yolu
* Satır numarası
* Önem seviyesi
* Açıklama
* Çözüm önerisi

Örnek bir bulgu aşağıdaki gibi olabilir:

```json
{
  "rule_id": "LONG_FUNCTION",
  "file": "example.py",
  "line": 10,
  "severity": "medium",
  "message": "Fonksiyon belirlenen satır sınırını aşıyor.",
  "suggestion": "Fonksiyonu daha küçük parçalara ayırın."
}
```

## Hata Yönetimi

Aşağıdaki hatalar kontrollü şekilde yönetilecektir:

* Dosyanın bulunamaması
* Dosyanın okunamaması
* Geçersiz Python sözdizimi
* Desteklenmeyen dosya türü
* Boş veya geçersiz klasör yolu

Bir dosyada hata oluşması durumunda hata mesajı gösterilecek ve mümkünse diğer dosyaların analizi devam edecektir.

## Prototip

İlk prototipte aşağıdaki işlemler yapılmaktadır:

* Örnek Python dosyası okunmaktadır.
* Kaynak kod AST yapısına dönüştürülmektedir.
* Normal ve asenkron fonksiyonlar bulunmaktadır.
* Fonksiyonların başlangıç ve bitiş satırları alınmaktadır.
* Fonksiyon uzunluğu hesaplanmaktadır.
* Belirlenen sınırı aşan fonksiyonlar raporlanmaktadır.

## Gelecek Geliştirmeler

* Komut satırı parametreleri
* Klasör ve alt klasör taraması
* Birden fazla analiz kuralı
* JSON raporu
* Unit testler
* Yapılandırılabilir kural sınırları
