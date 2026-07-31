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

## Mevcut Durum

Dependency scanner geliştirmesi başlamıştır. Ortak veri modelleri ve model
testleri tamamlanmıştır. Sıradaki aşama `requirements.txt` ayrıştırıcısının
geliştirilmesidir.## Navigation

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
