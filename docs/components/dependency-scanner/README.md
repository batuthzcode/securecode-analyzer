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

## Uygulanan Veri Modelleri

Dependency scanner bileşeninin ortak veri modelleri uygulanmıştır.

Oluşturulan Python paketi:

```text
src/dependency_scanner
```

Public modeller:

```python
from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
```

### Dependency

Bir `requirements.txt` satırından elde edilen sabitlenmiş Python
bağımlılığını temsil eder.

Alanlar:

- Paket adı
- Paket sürümü
- Sürüm operatörü
- Kaynak dosya
- Satır numarası

İlk sürümde yalnızca aşağıdaki operatör desteklenmektedir:

```text
==
```

### AdvisorySource

Güvenlik açığı bilgisinin kaynağını temsil eder.

Alanlar:

- Kaynak adı
- Opsiyonel kaynak bağlantısı

### VulnerabilitySeverity

Desteklenen güvenlik açığı önem seviyeleri:

```text
unknown
low
medium
high
critical
```

Güvenilir severity bilgisi bulunmadığında varsayılan değer:

```text
unknown
```

### DependencyFinding

Bir dependency ile onu etkileyen advisory kaydını birleştirir.

Bulgu içerisinde aşağıdaki bilgiler bulunur:

- Etkilenen dependency
- Advisory kimliği
- Açıklama
- Advisory kaynağı
- Severity
- Opsiyonel düzeltilmiş sürüm
- CVE veya GHSA gibi alternatif kimlikler

### Model Özellikleri

Bütün modeller:

- `dataclass` kullanır.
- `frozen=True` ile değiştirilemezdir.
- `slots=True` kullanır.
- Temel alan doğrulaması yapar.
- String değerlerin çevresindeki boşlukları temizler.
- JSON uyumlu sözlük üreten `to_dict()` metodu sağlar.
- Dosya sistemine veya internete erişmez.
- Static analyzer modellerinden bağımsızdır.

### Test Sonucu

Dependency model testleri:

```text
40 passed
```

Tam proje testleri:

```text
328 passed
```

SecureCode Analyzer self-analysis sonucu:

```text
No findings found.
```
## Uygulanan Requirements Parser

Dependency scanner bileşenine `requirements.txt` ayrıştırıcısı eklenmiştir.

Oluşturulan modül:

```text
src/dependency_scanner/requirements_parser.py
```

Test dosyası:

```text
tests/test_requirements_parser.py
```

### Public API

Parser bileşenleri paket seviyesinden kullanılabilir:

```python
from dependency_scanner import (
    RequirementsParseError,
    parse_requirement_line,
    parse_requirements_file,
    parse_requirements_text,
)
```

### Desteklenen Requirement Biçimi

İlk sürümde tam sürüm sabitlemesi desteklenmektedir:

```text
Flask==2.0.0
requests==2.25.0
example-package==1.4.2
```

Operatör çevresindeki boşluklar kabul edilmektedir:

```text
Flask == 2.0.0
```

Parser paket adının orijinal yazımını korur ve şu aşamada paket adı
normalizasyonu yapmaz.

### Atlanan Satırlar

Aşağıdaki satırlar dependency üretmeden atlanır:

- Boş satırlar
- Yalnızca whitespace içeren satırlar
- Tam satır yorumları
- Girintili tam satır yorumları

Örnek:

```text
# production dependencies

Flask==2.0.0
```

Bu örnekte `Flask` dependency kaydının satır numarası `3` olarak korunur.

### Üretilen Dependency Bilgileri

Her geçerli satır aşağıdaki alanlara sahip bir `Dependency` modeline
dönüştürülür:

- Paket adı
- Paket sürümü
- Sürüm operatörü
- Kaynak dosya yolu
- Bir tabanlı satır numarası

Sonuçlar requirements dosyasındaki kaynak sırasıyla tuple olarak döndürülür.

Parser:

- Sonuçları alfabetik olarak sıralamaz.
- Tekrarlanan paketleri kaldırmaz.
- Paket adlarını normalleştirmez.
- Sürümleri karşılaştırmaz.

### Parse Hataları

Desteklenmeyen aktif satırlar için:

```python
RequirementsParseError
```

üretilir.

Exception aşağıdaki bilgileri saklar:

- `source_file`
- `line_number`
- `line`
- `reason`

Örnek hata mesajı:

```text
requirements.txt:4: Unsupported requirement format.
```

İlk sürümde aşağıdaki biçimler desteklenmemektedir:

- `>=`, `~=`, `<` gibi farklı operatörler
- Inline yorumlar
- Environment marker ifadeleri
- Extras
- Requirements include satırları
- Constraint satırları
- Index seçenekleri
- Hash değerleri
- URL dependency kayıtları
- VCS dependency kayıtları
- Yerel paket yolları

### Dosya Okuma

`parse_requirements_file()`:

- Dosyayı UTF-8 olarak okur.
- Dosya yolunu dependency modellerine aktarır.
- İçeriği `parse_requirements_text()` ile ayrıştırır.
- Sonuçları tuple olarak döndürür.

Aşağıdaki operasyonel hatalar gizlenmez:

- `FileNotFoundError`
- `PermissionError`
- `IsADirectoryError`
- `UnicodeDecodeError`

### Test Sonuçları

Requirements parser testleri:

```text
38 passed
```

Tam proje testleri:

```text
366 passed
```

SecureCode Analyzer self-analysis sonucu:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```

## Mevcut Durum

Dependency scanner geliştirmesi devam etmektedir. Ortak veri modelleri ve
`requirements.txt` ayrıştırıcısı tamamlanmıştır.

Sıradaki aşama paket adı normalizasyonu ve vulnerability kaynağı istemci
arayüzünün geliştirilmesidir.

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
