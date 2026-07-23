# Static Code Analyzer - Analiz

## 1. Amaç

Static Code Analyzer bileşeninin amacı, Python kaynak kodlarını çalıştırmadan
inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit etmektir.

Araç, tespit ettiği problemlerin doğrudan hata olduğunu iddia etmek yerine
geliştirici tarafından incelenmesi gereken bulgular üretir.

## 2. Kapsam

Bileşenin temel kapsamı aşağıdaki işlemleri içerir:

- Tek bir Python dosyasını analiz etmek
- Bir klasör altındaki Python dosyalarını analiz etmek
- AST tabanlı kod kalite kurallarını çalıştırmak
- Metin tabanlı kontrolleri çalıştırmak
- Tespit edilen problemleri ortak bir bulgu modeliyle temsil etmek
- Bulguları terminalde göstermek
- Bulguları JSON formatında dışa aktarabilmek
- Analiz sonucuna göre uygun exit code üretmek

İlk sürümün amacı SonarQube gibi kapsamlı bir analiz platformu oluşturmak
değildir. Amaç, statik analiz sürecinin temel mantığını gösteren çalışan ve
genişletilebilir bir PoC hazırlamaktır.

## 3. Girdiler

Bileşen aşağıdaki girdileri kabul edecektir:

- Tek bir Python dosyasının yolu
- Bir Python proje klasörünün yolu
- Yapılandırılabilir kural eşikleri
- İsteğe bağlı çıktı formatı
- İsteğe bağlı çıktı dosyası

İlk aşamada yalnızca `.py` uzantılı dosyalar analiz edilecektir.

## 4. Fonksiyonel Gereksinimler

Statik analiz aracı aşağıdaki fonksiyonel gereksinimleri karşılamalıdır:

1. Kullanıcıdan dosya veya klasör yolu alabilmelidir.
2. Verilen klasör içindeki Python dosyalarını bulabilmelidir.
3. Python kaynak kodunu UTF-8 formatında okuyabilmelidir.
4. Kaynak kodu `ast.parse()` ile AST yapısına dönüştürebilmelidir.
5. Kayıtlı analiz kurallarını çalıştırabilmelidir.
6. Her kuralın ürettiği bulguları ortak bir listede toplayabilmelidir.
7. Bulguları terminalde gösterebilmelidir.
8. Bulguları JSON formatına dönüştürebilmelidir.
9. Dosya okuma ve sözdizimi hatalarını kontrollü şekilde yönetebilmelidir.
10. Yapılandırılan önem seviyesi eşiğine göre uygun exit code
    üretebilmelidir.
11. Aynı dosyada birden fazla bulgu üretebilmelidir.
12. Bir dosyadaki hata mümkünse diğer dosyaların analizini durdurmamalıdır.

## 5. Analiz Kuralları

| Kural | Durum | Yaklaşım | Gerekçe |
|---|---|---|---|
| Uzun fonksiyon | Uygulandı | AST | Fonksiyon başlangıç ve bitiş satırları yapısal olarak incelenir |
| Uzun sınıf | Planlandı | AST | Gerçek sınıf tanımlarının ve satır aralıklarının bulunması gerekir |
| Boş `except` bloğu | Planlandı | AST | Gerçek exception blokları incelenmelidir |
| Fonksiyon isimlendirme | Planlandı | AST | Fonksiyon tanımlarının isimleri kontrol edilir |
| Sınıf isimlendirme | Planlandı | AST | Sınıf tanımlarının isimleri kontrol edilir |
| `TODO` ve `FIXME` | Planlandı | Satır taraması | Yorumlar AST içerisinde doğrudan korunmaz |
| Hardcoded secret | Planlandı | Regex ve metin analizi | Şüpheli anahtar ve değer desenleri aranır |
| Bağlantı adresi | Planlandı | Regex ve metin analizi | Kaynak kod içerisindeki bağlantı desenleri aranır |

AST tabanlı kontroller, yorum veya string içerisindeki ifadeleri gerçek Python
yapılarıyla karıştırmamak için kullanılacaktır.

Metin tabanlı kontroller yanlış pozitif sonuçlar üretebilir. Özellikle
hardcoded secret bulguları doğrulanmış güvenlik açığı olarak değil, şüpheli
durum olarak raporlanacaktır.

## 6. Uzun Fonksiyon Kuralı

### 6.1 Amaç

Uzun fonksiyon kuralının amacı; okunması, test edilmesi ve bakımı
zorlaşabilecek fonksiyonları tespit etmektir.

Bir fonksiyonun uzun olması tek başına kesin bir hata değildir. Bu nedenle
kural, kodun hatalı olduğunu söylemek yerine geliştirici tarafından
incelenmesi gereken bir kod kalitesi bulgusu üretir.

### 6.2 Kural Bilgileri

Kural kimliği:

```text
SA001
```

Kural adı:

```text
Long Function
```

Varsayılan önem seviyesi:

```text
WARNING
```

### 6.3 Analiz Yöntemi

Kural Python'ın yerleşik `ast` modülünü kullanır.

AST tercih edilmesinin nedenleri:

- Gerçek fonksiyon tanımlarının güvenilir şekilde bulunabilmesi
- Normal ve asenkron fonksiyonların tespit edilebilmesi
- Yorum veya string içerisindeki `def` ifadelerinin dikkate alınmaması
- Fonksiyonların başlangıç ve bitiş satırlarının alınabilmesi
- İç içe tanımlanan fonksiyonların ayrı ayrı incelenebilmesi

Kural aşağıdaki AST düğümlerini kontrol eder:

- `ast.FunctionDef`
- `ast.AsyncFunctionDef`

### 6.4 Fonksiyon Uzunluğu Hesaplaması

Fonksiyon uzunluğu aşağıdaki AST bilgileri kullanılarak hesaplanır:

- `lineno`: fonksiyon tanımının başladığı satır
- `end_lineno`: fonksiyon tanımının bittiği satır

```text
fonksiyon uzunluğu = bitiş satırı - başlangıç satırı + 1
```

`end_lineno` bilgisinin bulunmadığı durumda başlangıç satırı kullanılır.

İlk sürümde başlangıç ve bitiş satırları arasındaki toplam fiziksel satır
sayısı dikkate alınır.

### 6.5 Varsayılan Eşik Değeri

Varsayılan eşik:

```text
50 satır
```

Fonksiyon uzunluğu eşik değerinden büyük olduğunda bulgu üretilir.

- 49 satırlık fonksiyon bulgu üretmez.
- 50 satırlık fonksiyon bulgu üretmez.
- 51 satırlık fonksiyon bulgu üretir.

Kural oluşturulurken özel bir eşik değeri verilebilir.

### 6.6 Eşik Doğrulaması

`max_lines` değeri pozitif bir tam sayı olmalıdır.

Aşağıdaki değerler reddedilir:

- `0`
- Negatif tam sayılar
- `True` ve `False`
- Ondalıklı sayılar
- Tam sayı olmayan diğer değerler

Geçersiz değerlerde `ValueError` üretilir.

### 6.7 Üretilecek Bulgu

Kural, eşik değerini aşan her fonksiyon için bir `Finding` nesnesi döndürür.

| Alan | Değer |
|---|---|
| `rule_id` | `SA001` |
| `message` | Fonksiyon adı, mevcut uzunluk ve izin verilen eşik |
| `file_path` | Analiz edilen dosyanın yolu |
| `line_number` | Fonksiyonun başladığı satır |
| `column_number` | AST düğümündeki `col_offset` değeri |
| `severity` | `WARNING` |

Örnek mesaj:

```text
Function 'process_data' has 64 lines, exceeding the limit of 50.
```

### 6.8 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamaktadır:

1. Normal Python fonksiyonlarını tespit eder.
2. Asenkron Python fonksiyonlarını tespit eder.
3. Eşik değerini aşan fonksiyon için bulgu üretir.
4. Eşik değerine eşit veya daha kısa fonksiyon için bulgu üretmez.
5. Özel bir eşik değeriyle çalışır.
6. Geçersiz eşik değerlerini reddeder.
7. Bulgunun kural kimliği `SA001` olur.
8. Bulgunun önem seviyesi `WARNING` olur.
9. Bulgunun dosya yolu, satır numarası ve sütun numarası doğru olur.
10. Birden fazla ve iç içe fonksiyon ayrı ayrı kontrol edilir.

### 6.9 Test Senaryoları

`LongFunctionRule` aşağıdaki senaryolarla doğrulanmıştır:

- Varsayılan eşik değeri
- Sıfır ve negatif eşik değerleri
- Boolean eşik değerleri
- Ondalıklı eşik değerleri
- Eşik değerine eşit fonksiyon
- Uzun normal fonksiyon
- Uzun asenkron fonksiyon
- Birden fazla uzun fonksiyon
- İç içe fonksiyonlar
- Bulgu alanları ve mesaj içeriği

## 7. Çıktı Gereksinimleri

Her bulgu için aşağıdaki bilgilerin üretilmesi beklenmektedir:

- Kural kimliği
- Kural adı
- Dosya yolu
- Satır numarası
- Varsa sütun numarası
- Önem seviyesi
- Problem açıklaması
- Çözüm önerisi

Mevcut `Finding` modelinde `rule_id`, `message`, `file_path`, `line_number`,
`severity` ve `column_number` alanları bulunmaktadır.

Kural adı ve çözüm önerisinin hangi katmanda tutulacağı, raporlama bileşeni
geliştirilirken netleştirilecektir.

## 8. Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır hata mesajlarıyla bildirilmelidir:

- Dosyanın bulunamaması
- Dosyanın okunamaması
- Geçersiz dosya uzantısı verilmesi
- Python sözdizimi hatası bulunması
- Geçersiz dosya veya klasör yolu verilmesi
- Boş klasör verilmesi
- Kaynak dosyanın UTF-8 olarak okunamaması
- Analiz kuralının beklenmeyen hata üretmesi

## 9. Fonksiyonel Olmayan Gereksinimler

### 9.1 Genişletilebilirlik

Yeni analiz kuralları mevcut kurallar değiştirilmeden eklenebilmelidir.

### 9.2 Test Edilebilirlik

Her analiz kuralı bağımsız unit testlerle doğrulanabilmelidir.

### 9.3 Okunabilirlik

Kod, anlaşılır sınıf ve fonksiyon isimleriyle geliştirilmelidir. Kamuya açık
sınıf ve fonksiyonlar açıklayıcı docstring içermelidir.

### 9.4 Güvenlik

Analiz edilen kaynak kod çalıştırılmamalıdır. Kaynak kod yalnızca metin ve AST
yapısı üzerinden incelenmelidir.

### 9.5 Taşınabilirlik

Araç Windows, Linux ve macOS ortamlarında çalışabilecek şekilde
geliştirilmelidir.

### 9.6 Performans

Her Python dosyası AST tabanlı kurallar için mümkün olduğunca yalnızca bir kez
parse edilmelidir.

## 10. Mevcut Durum

Tamamlanan çalışmalar:

- Statik analiz paket yapısı oluşturuldu.
- `Severity` enum yapısı oluşturuldu.
- `Finding` veri modeli oluşturuldu.
- Bulguların sözlük formatına dönüştürülmesi sağlandı.
- AST tabanlı kurallar için `BaseRule` arayüzü oluşturuldu.
- `LongFunctionRule` sınıfı geliştirildi.
- Normal ve asenkron fonksiyon desteği eklendi.
- İç içe fonksiyonların ayrı ayrı kontrol edilmesi sağlandı.
- Yapılandırılabilir satır sınırı eklendi.
- Geçersiz eşik değerleri için doğrulama eklendi.
- Uzun fonksiyon kuralı 10 test senaryosuyla doğrulandı.
- Projenin toplam 14 testi başarılı şekilde çalışmaktadır.

Henüz tamamlanmayan çalışmalar:

- Dosya ve klasör tarama mekanizması
- Analiz motoru
- Diğer analiz kuralları
- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- CI/CD entegrasyonu

## 11. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Teknik Tasarım](technical-design.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)