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
## Dependency Veri Modelleri Gereksinimleri

### Amaç

Dependency scanner bileşeninin farklı katmanlarında kullanılacak ortak veri
yapıları tanımlanacaktır.

Veri modelleri aşağıdaki işlemler arasında ortak bir sözleşme sağlayacaktır:

- `requirements.txt` ayrıştırma
- Dependency normalizasyonu
- OSV sorguları
- Advisory yanıtlarının işlenmesi
- Güvenlik açığı bulgularının oluşturulması
- Terminal çıktısı
- JSON çıktısı
- Unit ve entegrasyon testleri

Modeller aşağıdaki modülde bulunacaktır:

```text
src/dependency_scanner/models.py
```

Public modeller paket seviyesinden de dışa aktarılacaktır:

```python
from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
```

### Dependency Modeli

`Dependency` modeli, requirements dosyasından ayrıştırılan tek bir Python
bağımlılığını temsil edecektir.

Planlanan alanlar:

| Alan | Tip | Açıklama |
|---|---|---|
| `name` | `str` | Requirements dosyasında bulunan orijinal paket adı |
| `version` | `str` | Kullanılan sabitlenmiş paket sürümü |
| `operator` | `str` | İlk sürümde desteklenen sürüm operatörü |
| `source_file` | `str` | Dependency bilgisinin okunduğu dosya |
| `line_number` | `int` | Dependency satırının dosyadaki konumu |

İlk sürümde desteklenen operatör:

```text
==
```

Örnek:

```python
Dependency(
    name="Flask",
    version="2.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Model, paket adının requirements dosyasındaki orijinal biçimini koruyacaktır.

Paket adı normalizasyonu parser veya ayrı bir normalizasyon yardımcı fonksiyonu
tarafından gerçekleştirilecektir. Veri modelinin kendisi dosya okumamalı veya
requirements satırı ayrıştırmamalıdır.

### AdvisorySource Modeli

`AdvisorySource`, güvenlik açığı bilgisinin hangi kaynaktan geldiğini temsil
edecektir.

Planlanan alanlar:

| Alan | Tip | Açıklama |
|---|---|---|
| `name` | `str` | Kaynağın kullanıcı tarafından okunabilir adı |
| `url` | `str \| None` | Advisory veya kaynak bağlantısı |

Örnek:

```python
AdvisorySource(
    name="OSV",
    url="https://osv.dev/vulnerability/example",
)
```

Kaynak bağlantısı her advisory kaydında bulunmayabileceği için `url` alanı
opsiyonel olacaktır.

### VulnerabilitySeverity Enum Değeri

Dependency bulgularının önem seviyeleri `VulnerabilitySeverity` enum değeriyle
temsil edilecektir.

Desteklenen değerler:

```text
unknown
low
medium
high
critical
```

Enum, `str` sınıfından türetilecektir. Böylece değerler JSON çıktısına doğrudan
uygun metinsel değerlerle dönüştürülebilecektir.

Varsayılan önem seviyesi:

```text
unknown
```

Bir advisory kaydında güvenilir severity bilgisi bulunmadığında tahmini bir
seviye üretilmeyecektir.

Dependency scanner severity modeli, static analyzer bileşenindeki severity
modelinden bağımsız olacaktır.

### DependencyFinding Modeli

`DependencyFinding`, kullanılan bir dependency ile onu etkileyen advisory
kaydını birleştirecektir.

Planlanan alanlar:

| Alan | Tip | Açıklama |
|---|---|---|
| `dependency` | `Dependency` | Etkilenen dependency bilgisi |
| `advisory_id` | `str` | OSV, GHSA veya CVE gibi advisory kimliği |
| `message` | `str` | Güvenlik açığı açıklaması |
| `source` | `AdvisorySource` | Advisory bilgisinin kaynağı |
| `severity` | `VulnerabilitySeverity` | Önem seviyesi |
| `fixed_version` | `str \| None` | Biliniyorsa düzeltilmiş sürüm |
| `aliases` | `tuple[str, ...]` | CVE veya GHSA gibi alternatif kimlikler |

Örnek:

```python
DependencyFinding(
    dependency=Dependency(
        name="example-package",
        version="1.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=3,
    ),
    advisory_id="OSV-EXAMPLE",
    message="The installed version is affected.",
    source=AdvisorySource(
        name="OSV",
        url=None,
    ),
    severity=VulnerabilitySeverity.HIGH,
    fixed_version="1.0.1",
    aliases=("CVE-2099-0001",),
)
```

`fixed_version` her advisory kaydında bulunmayabilir. Bu durumda değer
`None` olacaktır.

`aliases` alanı bulunmayan kayıtlarda boş tuple kullanılacaktır.

### Değiştirilemez Veri Yapıları

Bütün dependency modelleri dataclass olarak tanımlanacaktır.

Aşağıdaki seçenekler kullanılacaktır:

```python
@dataclass(frozen=True, slots=True)
```

`frozen=True`, oluşturulan analiz verilerinin daha sonraki katmanlarda
yanlışlıkla değiştirilmesini engelleyecektir.

`slots=True`, modellerin tanımlanmamış alanlar almasını engelleyecek ve model
yapısını açık tutacaktır.

### JSON Dönüşümü

Her public model JSON uyumlu sözlük üretebilmelidir.

Planlanan public metot:

```python
to_dict()
```

`Dependency.to_dict()` örneği:

```json
{
  "name": "Flask",
  "version": "2.0.0",
  "operator": "==",
  "source_file": "requirements.txt",
  "line_number": 1
}
```

`AdvisorySource.to_dict()` örneği:

```json
{
  "name": "OSV",
  "url": null
}
```

`DependencyFinding.to_dict()` örneği:

```json
{
  "dependency": {
    "name": "example-package",
    "version": "1.0.0",
    "operator": "==",
    "source_file": "requirements.txt",
    "line_number": 3
  },
  "advisory_id": "OSV-EXAMPLE",
  "message": "The installed version is affected.",
  "source": {
    "name": "OSV",
    "url": null
  },
  "severity": "high",
  "fixed_version": "1.0.1",
  "aliases": [
    "CVE-2099-0001"
  ]
}
```

Enum değerleri kendi küçük harfli string değerleriyle gösterilecektir.

Tuple alanları JSON uyumluluğu için listelere dönüştürülecektir.

### Girdi Doğrulaması

Modeller en az aşağıdaki geçersiz değerleri reddetmelidir:

- Boş dependency adı
- Boş dependency sürümü
- Desteklenmeyen veya boş sürüm operatörü
- Boş kaynak dosya yolu
- Sıfır veya negatif satır numarası
- Boş advisory source adı
- Boş advisory kimliği
- Boş bulgu mesajı
- Boş fixed version değeri
- Boş alias değerleri

Geçersiz model verileri için:

```text
ValueError
```

üretilmelidir.

String değerlerinin başında ve sonunda bulunan gereksiz boşluklar model
oluşturulurken temizlenebilir.

Model doğrulaması:

- Dosya sistemine erişmemelidir.
- İnternet isteği yapmamalıdır.
- OSV verisi sorgulamamalıdır.
- Paket sürümlerini karşılaştırmamalıdır.
- Requirements satırlarını ayrıştırmamalıdır.

### Sorumluluk Sınırları

Dependency modelleri yalnızca veri temsilinden ve kendi alanlarının temel
doğrulamasından sorumludur.

Bu aşamada modeller:

- `requirements.txt` dosyası okumayacaktır.
- Paket adı normalizasyonu yapmayacaktır.
- Version karşılaştırması yapmayacaktır.
- OSV API isteği göndermeyecektir.
- Advisory JSON yanıtı ayrıştırmayacaktır.
- Terminal çıktısı üretmeyecektir.
- JSON dosyası yazmayacaktır.
- Exit code hesaplamayacaktır.
- Static analyzer modellerine bağımlı olmayacaktır.

### Paket Yapısı

Planlanan dosyalar:

```text
src/dependency_scanner/__init__.py
src/dependency_scanner/models.py
tests/test_dependency_models.py
```

`__init__.py` aşağıdaki public importları sağlayacaktır:

```python
from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
```

### Test Gereksinimleri

Testler en az aşağıdaki davranışları doğrulamalıdır:

- Bütün modellerin geçerli verilerle oluşturulması
- Modellerin `frozen` olması
- Modellerin `slots` kullanması
- Severity enum değerleri
- Varsayılan `unknown` severity
- Opsiyonel source URL davranışı
- Opsiyonel fixed version davranışı
- Varsayılan boş aliases tuple değeri
- Dependency JSON dönüşümü
- Advisory source JSON dönüşümü
- Dependency finding JSON dönüşümü
- Enum değerinin string olarak dönüştürülmesi
- Alias tuple değerinin JSON listesine dönüştürülmesi
- Nested dependency ve source dönüşümü
- Boş zorunlu string alanlarının reddedilmesi
- Geçersiz line number değerlerinin reddedilmesi
- Desteklenmeyen operator değerlerinin reddedilmesi
- Boş fixed version değerinin reddedilmesi
- Boş alias değerinin reddedilmesi
- Public package importları
- Modellerin birbirinden bağımsız örnekler olması

Unit testler internet bağlantısına ihtiyaç duymamalıdır.

### Kabul Kriterleri

1. `dependency_scanner` Python paketi oluşturulmalıdır.
2. `Dependency` modeli uygulanmalıdır.
3. `AdvisorySource` modeli uygulanmalıdır.
4. `VulnerabilitySeverity` enum değeri uygulanmalıdır.
5. `DependencyFinding` modeli uygulanmalıdır.
6. Modeller `frozen` ve `slots` kullanmalıdır.
7. Modeller temel girdi doğrulaması yapmalıdır.
8. Modeller JSON uyumlu sözlük üretebilmelidir.
9. Public modeller paket seviyesinden import edilebilmelidir.
10. Modeller static analyzer paketine bağımlı olmamalıdır.
11. Unit testler dış servislere bağlanmamalıdır.
12. Bütün mevcut proje testleri geçmeye devam etmelidir.

### Planlanan Git Commitleri

```text
docs(dependency-scanner): define data model requirements
feat(dependency-scanner): add core data models
docs(dependency-scanner): document core data models
## Gerçekleştirilen Dependency Veri Modelleri

Dependency scanner için planlanan temel veri modelleri uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/__init__.py
src/dependency_scanner/models.py
tests/test_dependency_models.py
```

### Dependency Modeli

`Dependency` modeli aşağıdaki alanlarla uygulanmıştır:

| Alan | Tip |
|---|---|
| `name` | `str` |
| `version` | `str` |
| `operator` | `str` |
| `source_file` | `str` |
| `line_number` | `int` |

Model aşağıdaki doğrulamaları yapmaktadır:

- Paket adı boş olamaz.
- Paket sürümü boş olamaz.
- Kaynak dosya yolu boş olamaz.
- Satır numarası pozitif tam sayı olmalıdır.
- `bool` değeri satır numarası olarak kabul edilmez.
- İlk sürümde yalnızca `==` operatörü kabul edilir.

String alanlarının başındaki ve sonundaki gereksiz boşluklar temizlenmektedir.

### AdvisorySource Modeli

`AdvisorySource` modeli aşağıdaki alanlarla uygulanmıştır:

| Alan | Tip |
|---|---|
| `name` | `str` |
| `url` | `str \| None` |

Kaynak adı zorunludur. Kaynak bağlantısı opsiyoneldir.

Bir URL değeri verilmişse boş veya yalnızca boşluk karakterlerinden oluşamaz.

### VulnerabilitySeverity Enum Değeri

Aşağıdaki değerler uygulanmıştır:

```text
unknown
low
medium
high
critical
```

Enum, string tabanlıdır ve JSON dönüşümünde küçük harfli değerlerini kullanır.

### DependencyFinding Modeli

`DependencyFinding` aşağıdaki alanlarla uygulanmıştır:

| Alan | Tip |
|---|---|
| `dependency` | `Dependency` |
| `advisory_id` | `str` |
| `message` | `str` |
| `source` | `AdvisorySource` |
| `severity` | `VulnerabilitySeverity` |
| `fixed_version` | `str \| None` |
| `aliases` | `tuple[str, ...]` |

Varsayılan değerler:

```text
severity = unknown
fixed_version = None
aliases = ()
```

Model, nested alanların doğru model tiplerini kullanmasını doğrulamaktadır.

Aşağıdaki geçersiz değerler reddedilmektedir:

- Boş advisory kimliği
- Boş bulgu mesajı
- Boş fixed version
- Boş alias
- Tuple olmayan aliases değeri
- `Dependency` olmayan dependency değeri
- `AdvisorySource` olmayan source değeri
- Geçersiz severity tipi

### JSON Dönüşümü

Bütün modeller `to_dict()` metodu sağlamaktadır.

`DependencyFinding.to_dict()`:

- Dependency modelini nested sözlüğe dönüştürür.
- Advisory source modelini nested sözlüğe dönüştürür.
- Severity enum değerini string olarak üretir.
- Alias tuple değerini JSON uyumlu listeye dönüştürür.
- Opsiyonel alanlarda `None` değerini korur.

### Değiştirilemezlik

Bütün modeller aşağıdaki dataclass seçenekleriyle uygulanmıştır:

```python
@dataclass(frozen=True, slots=True)
```

Bu sayede:

- Model alanları oluşturulduktan sonra değiştirilemez.
- Dinamik ve tanımlanmamış alanlar eklenemez.
- Model sözleşmesi açık kalır.

### Sorumluluk Sınırları

Veri modelleri:

- Requirements dosyası okumaz.
- Requirements satırı ayrıştırmaz.
- Paket adı normalizasyonu yapmaz.
- Paket sürümü karşılaştırmaz.
- OSV API isteği göndermez.
- Advisory API yanıtı ayrıştırmaz.
- Terminal çıktısı üretmez.
- JSON dosyası yazmaz.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

Model testleri:

```text
40 passed
```

Tam test paketi:

```text
328 passed
```

Derleme kontrolü:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
```

Derleme işlemi hata üretmemiştir.

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```

İlk uygulamada iki uzun `__post_init__()` bulgusu tespit edilmiştir.

Bu bulgular analiz eşiği değiştirilmeden, doğrulama ve temizleme işlemlerinin
küçük yardımcı fonksiyonlara ayrılmasıyla giderilmiştir.
## Requirements Parser Gereksinimleri

### Amaç

Requirements Parser, bir Python projesindeki `requirements.txt` dosyasını
okuyarak desteklenen dependency satırlarını `Dependency` modellerine
dönüştürecektir.

Planlanan dosyalar:

```text
src/dependency_scanner/requirements_parser.py
tests/test_requirements_parser.py
```
## Gerçekleştirilen Requirements Parser

Dependency scanner için exact-pin requirements ayrıştırıcısı uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/requirements_parser.py
tests/test_requirements_parser.py
```

Mevcut paket export dosyası güncellenmiştir:

```text
src/dependency_scanner/__init__.py
```

### Public Bileşenler

Aşağıdaki bileşenler `dependency_scanner` paketi üzerinden dışa
aktarılmaktadır:

```python
from dependency_scanner import (
    RequirementsParseError,
    parse_requirement_line,
    parse_requirements_file,
    parse_requirements_text,
)
```

### Satır Ayrıştırma

`parse_requirement_line()` tek bir requirements satırını işler.

Geçerli örnek:

```text
Flask==2.0.0
```

Üretilen model:

```python
Dependency(
    name="Flask",
    version="2.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Operatör çevresindeki boşluklar kabul edilmektedir:

```text
Flask == 2.0.0
```

Paket adı ve sürüm değeri çevresindeki gereksiz boşluklar ayrıştırma sırasında
temizlenmektedir.

### Desteklenen Paket Adları

İlk uygulama aşağıdaki karakterleri içeren paket adlarını desteklemektedir:

- Harf
- Rakam
- Tire
- Alt çizgi
- Nokta

Örnekler:

```text
example-package
example_package
example.package
package2
```

Paket adı normalizasyonu parser sorumluluğuna dahil edilmemiştir.

### Boş ve Yorum Satırları

Aşağıdaki satırlar için `None` döndürülmektedir:

- Boş satırlar
- Whitespace-only satırlar
- İlk görünür karakteri `#` olan tam satır yorumları

Metin ayrıştırma sırasında bu satırlar sonuç tuple değerine eklenmez.

### Metin Ayrıştırma

`parse_requirements_text()`:

1. Metni satırlara ayırır.
2. Satır numaralarını `1` değerinden başlatır.
3. Satırları kaynak sırasıyla işler.
4. Boş ve yorum satırlarını atlar.
5. Aktif satırları `parse_requirement_line()` ile ayrıştırır.
6. Sonuçları tuple olarak döndürür.

Boş ve yorum satırları satır numarası hesaplamasından çıkarılmaz.

Parser dependency kayıtlarını sıralamaz veya tekrarları kaldırmaz.

### Dosya Ayrıştırma

`parse_requirements_file()`:

1. Girdiyi `Path` nesnesine dönüştürür.
2. Dosyayı UTF-8 olarak okur.
3. İçeriği `parse_requirements_text()` fonksiyonuna gönderir.
4. Dosya yolunu dependency modellerine aktarır.
5. Sonuçları tuple olarak döndürür.

Operasyonel dosya hataları parser hatasına dönüştürülmez.

Korunan hata türleri:

```text
FileNotFoundError
PermissionError
IsADirectoryError
UnicodeDecodeError
```

### RequirementsParseError

Desteklenmeyen aktif requirements satırları
`RequirementsParseError` üretmektedir.

Exception alanları:

| Alan | Açıklama |
|---|---|
| `source_file` | Hatanın bulunduğu requirements dosyası |
| `line_number` | Bir tabanlı satır numarası |
| `line` | Orijinal satır içeriği |
| `reason` | Kullanıcı tarafından okunabilir hata nedeni |

Örnek mesaj:

```text
requirements.txt:4: Unsupported requirement format.
```

Orijinal satır exception alanında saklanır ancak hata mesajında gereksiz
şekilde tekrar edilmez.

### Reddedilen Biçimler

İlk uygulamada aşağıdaki biçimler reddedilmektedir:

```text
==1.2.3
Flask==
Flask>=2.0.0
Flask~=2.0.0
Flask<3.0.0
Flask==2.0.0 # comment
Flask==2.0.0; python_version >= "3.11"
requests[security]==2.25.0
-r base-requirements.txt
-c constraints.txt
--index-url https://example.com/simple
Flask==2.0.0 --hash=sha256:example
package @ https://example.com/package.whl
git+https://example.com/repository.git
../local-package
```

Bu biçimler gelecekte ayrı geliştirmelerle desteklenebilir.

### Sorumluluk Sınırları

Requirements parser:

- Paket adı normalizasyonu yapmaz.
- Paket sürümü karşılaştırmaz.
- Duplicate dependency politikası uygulamaz.
- OSV API isteği göndermez.
- Advisory kayıtlarını ayrıştırmaz.
- Güvenlik açığı bulgusu oluşturmaz.
- Terminal raporu üretmez.
- JSON dosyası yazmaz.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

Requirements parser testleri:

```text
38 passed
```

Tam test paketi:

```text
366 passed
```

Derleme kontrolü:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
```

Derleme kontrolü hata üretmemiştir.

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```

## Navigation

- [Dependency Scanner sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)