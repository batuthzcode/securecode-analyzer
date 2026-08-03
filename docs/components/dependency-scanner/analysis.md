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
## Paket Adı Normalizasyonu Gereksinimleri

### Amaç

Paket adı normalizasyonu, farklı yazım biçimleriyle belirtilen aynı Python
paketinin güvenlik açığı kaynaklarında ortak bir adla sorgulanmasını
sağlayacaktır.

Örneğin aşağıdaki adlar aynı normalize edilmiş paket adına dönüşmelidir:

```text
Sample-Package
sample_package
sample.package
sample---package
```

Beklenen normalize edilmiş değer:

```text
sample-package
```

Planlanan modül:

```text
src/dependency_scanner/package_normalizer.py
```

Planlanan testPlanlanan modül:

```text
src/dependency_scanner/package_normalizer.py
```

Planlanan test dosyası:

```text
tests/test_package_normalizer.py
```

### Public API

Normalizasyon fonksiyonu paket seviyesinden import edilebilmelidir:

```python
from dependency_scanner import normalize_package_name
```

Planlanan fonksiyon imzası:

```python
def normalize_package_name(name: str) -> str:
    ...
```

Fonksiyon yalnızca paket adını almalı ve normalize edilmiş string değeri
döndürmelidir.

### Normalizasyon Kuralları

Paket adı aşağıdaki sırayla normalize edilmelidir:

1. Başındaki ve sonundaki whitespace temizlenmelidir.
2. Bütün harfler küçük harfe dönüştürülmelidir.
3. Ardışık tire, alt çizgi ve nokta karakterleri tek tireye dönüştürülmelidir.
4. Paket adının diğer geçerli karakterleri korunmalıdır.

Dönüştürülecek ayırıcı karakterler:

```text
-
_
.
```

Örnekler:

| Girdi | Sonuç |
|---|---|
| `Flask` | `flask` |
| `Requests` | `requests` |
| `sample-package` | `sample-package` |
| `sample_package` | `sample-package` |
| `sample.package` | `sample-package` |
| `Sample_Package` | `sample-package` |
| `sample---package` | `sample-package` |
| `sample__package` | `sample-package` |
| `sample..package` | `sample-package` |
| `sample-_.package` | `sample-package` |
| `package2` | `package2` |
| `Package2_Name` | `package2-name` |

### Orijinal Paket Adının Korunması

`Dependency.name` alanı requirements dosyasında bulunan orijinal paket adını
korumaya devam etmelidir.

Örnek:

```python
dependency = Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Normalizasyon sonrasında `dependency.name` değiştirilmemelidir.

Bunun yerine:

```python
normalized_name = normalize_package_name(
    dependency.name
)
```

kullanılmalıdır.

Beklenen:

```text
dependency.name == "Sample_Package"
normalized_name == "sample-package"
```

Normalizasyon fonksiyonu `Dependency` modelini değiştirmemeli veya yeni bir
`Dependency` örneği oluşturmamalıdır.

### Girdi Doğrulaması

Fonksiyon aşağıdaki geçersiz girdileri reddetmelidir:

- String olmayan değer
- Boş string
- Yalnızca whitespace içeren string
- Yalnızca ayırıcı karakterlerden oluşan paket adı
- Normalize edildiğinde boş kalan değer

Geçersiz girdiler için:

```text
ValueError
```

üretilmelidir.

Örnek geçersiz değerler:

```text
""
"   "
"-"
"_"
"."
"-_."
```

String olmayan girdiler de `ValueError` üretmelidir.

### Geçerli Karakterler

İlk sürümde normalize edilecek paket adı:

- ASCII harf içerebilir.
- Rakam içerebilir.
- Tire içerebilir.
- Alt çizgi içerebilir.
- Nokta içerebilir.

Normalizasyon fonksiyonu requirements satırı ayrıştırmamalıdır.

Desteklenmeyen karakterler içeren adlar reddedilmelidir.

Örnek geçersiz adlar:

```text
package name
package/name
package@name
package#name
```

### Deterministik Davranış

Aynı paket adı her çağrıda aynı sonucu üretmelidir.

Normalizasyon idempotent olmalıdır:

```python
normalized = normalize_package_name(
    "Sample_Package"
)

assert normalize_package_name(
    normalized
) == normalized
```

Fonksiyon:

- Dosya sistemine erişmemelidir.
- İnternet isteği göndermemelidir.
- Global state değiştirmemelidir.
- Dependency listesini değiştirmemelidir.
- Paket sürümünü incelememelidir.

### Parser ile Sorumluluk Ayrımı

Requirements parser paket adının orijinal yazımını korumaya devam etmelidir.

Örnek requirements satırı:

```text
Sample_Package==1.0.0
```

Parser sonucu:

```python
Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Normalizasyon ancak güvenlik açığı kaynağına sorgu hazırlanırken veya paket
adlarının karşılaştırılması gerektiğinde açıkça uygulanmalıdır.

Parser içinde otomatik normalizasyon yapılmamalıdır.

### Paket Exportu

Aşağıdaki import çalışmalıdır:

```python
from dependency_scanner import normalize_package_name
```

Mevcut model ve requirements parser exportları korunmalıdır.

### Test Gereksinimleri

Unit testler en az aşağıdaki davranışları doğrulamalıdır:

- Büyük harflerin küçük harfe çevrilmesi
- Küçük harfli adın korunması
- Tireli adın normalize edilmesi
- Alt çizginin tireye dönüştürülmesi
- Noktanın tireye dönüştürülmesi
- Ardışık tirelerin tek tireye dönüştürülmesi
- Ardışık alt çizgilerin tek tireye dönüştürülmesi
- Ardışık noktaların tek tireye dönüştürülmesi
- Karışık ayırıcıların tek tireye dönüştürülmesi
- Rakamların korunması
- Baş ve son whitespace temizliği
- Aynı paketin farklı yazımlarının aynı sonuca dönüşmesi
- Normalize edilmiş adın tekrar normalize edilmesi
- Orijinal `Dependency.name` değerinin değişmemesi
- Boş adın reddedilmesi
- Whitespace-only adın reddedilmesi
- Yalnızca ayırıcı içeren adın reddedilmesi
- String olmayan değerin reddedilmesi
- Whitespace içeren paket adının reddedilmesi
- Slash içeren paket adının reddedilmesi
- `@` içeren paket adının reddedilmesi
- Public package exportu
- Testlerin internet bağlantısı gerektirmemesi

### Sorumluluk Sınırları

Paket adı normalizasyonu:

- Requirements dosyası okumayacaktır.
- Requirements satırı ayrıştırmayacaktır.
- `Dependency` modelini değiştirmeyecektir.
- Paket sürümü karşılaştırmayacaktır.
- Duplicate dependency tespiti yapmayacaktır.
- OSV API isteği göndermeyecektir.
- Advisory cevabı ayrıştırmayacaktır.
- Güvenlik açığı bulgusu oluşturmayacaktır.
- Terminal veya JSON raporu üretmeyecektir.
- Exit code hesaplamayacaktır.
- Static analyzer paketine bağımlı olmayacaktır.

### Kabul Kriterleri

1. `package_normalizer.py` modülü oluşturulmalıdır.
2. `normalize_package_name()` fonksiyonu uygulanmalıdır.
3. Paket adları küçük harfe dönüştürülmelidir.
4. Tire, alt çizgi ve nokta grupları tek tireye dönüştürülmelidir.
5. Orijinal `Dependency.name` değeri değiştirilmemelidir.
6. Geçersiz girdiler açık hata üretmelidir.
7. Normalizasyon deterministik ve idempotent olmalıdır.
8. Public fonksiyon paket seviyesinden export edilmelidir.
9. Unit testler dış servis kullanmamalıdır.
10. Requirements parser davranışı korunmalıdır.
11. Bütün mevcut proje testleri geçmelidir.
12. SecureCode Analyzer self-analysis sonucu temiz olmalıdır.

### Planlanan Git Commitleri

```text
docs(dependency-scanner): define package normalization requirements
feat(dependency-scanner): add package name normalization
docs(dependency-scanner): document package name normalization
```
## Gerçekleştirilen Paket Adı Normalizasyonu

Python paket adlarının güvenlik açığı kaynaklarında güvenilir biçimde
karşılaştırılabilmesi için paket adı normalizasyonu uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/package_normalizer.py
tests/test_package_normalizer.py
```

Public paket export dosyası güncellenmiştir:

```text
src/dependency_scanner/__init__.py
```

### Public Fonksiyon

Aşağıdaki fonksiyon `dependency_scanner` paketinden dışa aktarılmaktadır:

```python
from dependency_scanner import normalize_package_name
```

Fonksiyon imzası:

```python
def normalize_package_name(name: str) -> str:
    ...
```

### Normalizasyon Akışı

`normalize_package_name()` aşağıdaki işlemleri uygular:

1. Girdinin string olduğunu doğrular.
2. Başındaki ve sonundaki whitespace değerlerini temizler.
3. Paket adının yalnızca desteklenen karakterleri içerdiğini doğrular.
4. Ardışık tire, alt çizgi ve nokta karakterlerini tek tireye dönüştürür.
5. Büyük harfleri küçük harfe dönüştürür.
6. Sonucun en az bir alfanümerik karakter içerdiğini doğrular.
7. Normalize edilmiş string değerini döndürür.

Ayırıcı normalizasyonu için aşağıdaki karakter grubu kullanılmaktadır:

```text
[-_.]+
```

Bu grup tek tire karakterine dönüştürülmektedir.

### Normalizasyon Örnekleri

| Girdi | Sonuç |
|---|---|
| `Flask` | `flask` |
| `requests` | `requests` |
| `sample-package` | `sample-package` |
| `sample_package` | `sample-package` |
| `sample.package` | `sample-package` |
| `Sample_Package` | `sample-package` |
| `sample---package` | `sample-package` |
| `sample__package` | `sample-package` |
| `sample..package` | `sample-package` |
| `sample-_.package` | `sample-package` |
| `package2` | `package2` |
| `Package2_Name` | `package2-name` |

Aşağıdaki farklı yazımlar aynı sonucu üretmektedir:

```text
Sample-Package
sample_package
sample.package
sample---package
```

Normalize edilmiş sonuç:

```text
sample-package
```

### Orijinal Paket Adının Korunması

Normalizasyon `Dependency` modelinin içinde otomatik olarak yapılmamaktadır.

Örnek:

```python
dependency = Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)

normalized_name = normalize_package_name(
    dependency.name
)
```

Doğrulanan sonuç:

```text
dependency.name == "Sample_Package"
normalized_name == "sample-package"
```

Bu ayrım sayesinde:

- Requirements dosyasındaki orijinal yazım korunur.
- Kullanıcıya gösterilecek dependency bilgisi değiştirilmez.
- Güvenlik açığı sorgusu için normalize edilmiş ad ayrıca üretilebilir.
- Parser ile normalizasyon sorumlulukları birbirinden ayrılır.

### Girdi Doğrulaması

Fonksiyon aşağıdaki değerleri reddetmektedir:

- String olmayan değer
- Boş string
- Whitespace-only string
- Yalnızca tire, alt çizgi veya noktadan oluşan değer
- İç whitespace içeren değer
- Slash içeren değer
- `@`, `#` veya `:` gibi desteklenmeyen karakterler
- ASCII paket adı kapsamı dışındaki karakterler

Geçersiz örnekler:

```text
""
" "
"-"
"_"
"."
"-_."
"package name"
"package/name"
"package@name"
"package#name"
```

Geçersiz girdilerde `ValueError` üretilmektedir.

### Deterministik Davranış

Normalizasyon fonksiyonu global state kullanmamaktadır.

Aynı girdi her çağrıda aynı sonucu üretmektedir.

Örnek:

```python
first_result = normalize_package_name(
    "Sample_Package"
)
second_result = normalize_package_name(
    "Sample_Package"
)

assert first_result == second_result
```

### Idempotent Davranış

Normalize edilmiş paket adı tekrar normalize edildiğinde değişmemektedir:

```python
normalized_name = normalize_package_name(
    "Sample_Package"
)

assert normalize_package_name(
    normalized_name
) == normalized_name
```

### Parser ile Entegrasyon Sınırı

Requirements parser paket adının orijinal biçimini korumaktadır.

Örnek requirements satırı:

```text
Sample_Package==1.0.0
```

Parser sonucu:

```python
Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Normalizasyon parser içinde otomatik olarak uygulanmamaktadır.

Güvenlik açığı kaynağına sorgu hazırlanırken aşağıdaki biçimde açıkça
uygulanabilecektir:

```python
package_name = normalize_package_name(
    dependency.name
)
```

### Sorumluluk Sınırları

Paket adı normalizasyonu:

- Requirements dosyası okumaz.
- Requirements satırı ayrıştırmaz.
- Dependency modelini değiştirmez.
- Yeni Dependency modeli oluşturmaz.
- Paket sürümü karşılaştırmaz.
- Duplicate dependency politikası uygulamaz.
- OSV API isteği göndermez.
- Advisory cevabı ayrıştırmaz.
- Güvenlik açığı bulgusu oluşturmaz.
- Terminal raporu üretmez.
- JSON dosyası yazmaz.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

Paket adı normalizasyon testleri:

```text
38 passed
```

Tam test paketi:

```text
404 passed
```

Derleme doğrulaması:

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
## Gerçekleştirilen Paket Adı Normalizasyonu

Python paket adlarının güvenlik açığı kaynaklarında güvenilir biçimde
karşılaştırılabilmesi için paket adı normalizasyonu uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/package_normalizer.py
tests/test_package_normalizer.py
```

Public paket export dosyası güncellenmiştir:

```text
src/dependency_scanner/__init__.py
```

### Public Fonksiyon

Aşağıdaki fonksiyon `dependency_scanner` paketinden dışa aktarılmaktadır:

```python
from dependency_scanner import normalize_package_name
```

Fonksiyon imzası:

```python
def normalize_package_name(name: str) -> str:
    ...
```

### Normalizasyon Akışı

`normalize_package_name()` aşağıdaki işlemleri uygular:

1. Girdinin string olduğunu doğrular.
2. Başındaki ve sonundaki whitespace değerlerini temizler.
3. Paket adının yalnızca desteklenen karakterleri içerdiğini doğrular.
4. Ardışık tire, alt çizgi ve nokta karakterlerini tek tireye dönüştürür.
5. Büyük harfleri küçük harfe dönüştürür.
6. Sonucun en az bir alfanümerik karakter içerdiğini doğrular.
7. Normalize edilmiş string değerini döndürür.

Ayırıcı normalizasyonu için aşağıdaki karakter grubu kullanılmaktadır:

```text
[-_.]+
```

Bu grup tek tire karakterine dönüştürülmektedir.

### Normalizasyon Örnekleri

| Girdi | Sonuç |
|---|---|
| `Flask` | `flask` |
| `requests` | `requests` |
| `sample-package` | `sample-package` |
| `sample_package` | `sample-package` |
| `sample.package` | `sample-package` |
| `Sample_Package` | `sample-package` |
| `sample---package` | `sample-package` |
| `sample__package` | `sample-package` |
| `sample..package` | `sample-package` |
| `sample-_.package` | `sample-package` |
| `package2` | `package2` |
| `Package2_Name` | `package2-name` |

Aşağıdaki farklı yazımlar aynı sonucu üretmektedir:

```text
Sample-Package
sample_package
sample.package
sample---package
```

Normalize edilmiş sonuç:

```text
sample-package
```

### Orijinal Paket Adının Korunması

Normalizasyon `Dependency` modelinin içinde otomatik olarak yapılmamaktadır.

Örnek:

```python
dependency = Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)

normalized_name = normalize_package_name(
    dependency.name
)
```

Doğrulanan sonuç:

```text
dependency.name == "Sample_Package"
normalized_name == "sample-package"
```

Bu ayrım sayesinde:

- Requirements dosyasındaki orijinal yazım korunur.
- Kullanıcıya gösterilecek dependency bilgisi değiştirilmez.
- Güvenlik açığı sorgusu için normalize edilmiş ad ayrıca üretilebilir.
- Parser ile normalizasyon sorumlulukları birbirinden ayrılır.

### Girdi Doğrulaması

Fonksiyon aşağıdaki değerleri reddetmektedir:

- String olmayan değer
- Boş string
- Whitespace-only string
- Yalnızca tire, alt çizgi veya noktadan oluşan değer
- İç whitespace içeren değer
- Slash içeren değer
- `@`, `#` veya `:` gibi desteklenmeyen karakterler
- ASCII paket adı kapsamı dışındaki karakterler

Geçersiz örnekler:

```text
""
" "
"-"
"_"
"."
"-_."
"package name"
"package/name"
"package@name"
"package#name"
```

Geçersiz girdilerde `ValueError` üretilmektedir.

### Deterministik Davranış

Normalizasyon fonksiyonu global state kullanmamaktadır.

Aynı girdi her çağrıda aynı sonucu üretmektedir.

Örnek:

```python
first_result = normalize_package_name(
    "Sample_Package"
)
second_result = normalize_package_name(
    "Sample_Package"
)

assert first_result == second_result
```

### Idempotent Davranış

Normalize edilmiş paket adı tekrar normalize edildiğinde değişmemektedir:

```python
normalized_name = normalize_package_name(
    "Sample_Package"
)

assert normalize_package_name(
    normalized_name
) == normalized_name
```

### Parser ile Entegrasyon Sınırı

Requirements parser paket adının orijinal biçimini korumaktadır.

Örnek requirements satırı:

```text
Sample_Package==1.0.0
```

Parser sonucu:

```python
Dependency(
    name="Sample_Package",
    version="1.0.0",
    operator="==",
    source_file="requirements.txt",
    line_number=1,
)
```

Normalizasyon parser içinde otomatik olarak uygulanmamaktadır.

Güvenlik açığı kaynağına sorgu hazırlanırken aşağıdaki biçimde açıkça
uygulanabilecektir:

```python
package_name = normalize_package_name(
    dependency.name
)
```

### Sorumluluk Sınırları

Paket adı normalizasyonu:

- Requirements dosyası okumaz.
- Requirements satırı ayrıştırmaz.
- Dependency modelini değiştirmez.
- Yeni Dependency modeli oluşturmaz.
- Paket sürümü karşılaştırmaz.
- Duplicate dependency politikası uygulamaz.
- OSV API isteği göndermez.
- Advisory cevabı ayrıştırmaz.
- Güvenlik açığı bulgusu oluşturmaz.
- Terminal raporu üretmez.
- JSON dosyası yazmaz.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

Paket adı normalizasyon testleri:

```text
38 passed
```

Tam test paketi:

```text
404 passed
```

Derleme doğrulaması:

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
## Vulnerability Source Interface Gereksinimleri

### Amaç

Vulnerability source interface, dependency bilgilerini farklı güvenlik açığı
kaynaklarında sorgulayan bileşenler için ortak bir sözleşme sağlayacaktır.

Bu arayüz sayesinde dependency scanner:

- Belirli bir API sağlayıcısına doğrudan bağımlı olmayacaktır.
- OSV gibi gerçek kaynaklar sonradan ayrı sınıflarla uygulanabilecektir.
- Unit testlerde internet gerektirmeyen sahte kaynaklar kullanılabilecektir.
- Tarama akışı kaynak uygulamasından bağımsız geliştirilebilecektir.
- Yeni güvenlik açığı kaynakları mevcut tarama kodu değiştirilmeden
  eklenebilecektir.

Planlanan modül:

```text
src/dependency_scanner/vulnerability_source.py
```

Planlanan test dosyası:

```text
tests/test_vulnerability_source.py
```

### Public API

Aşağıdaki arayüz paket seviyesinden import edilebilmelidir:

```python
from dependency_scanner import VulnerabilitySource
```

Planlanan sözleşme:

```python
class VulnerabilitySource(Protocol):
    @property
    def advisory_source(self) -> AdvisorySource:
        ...

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        ...
```

Arayüz `typing.Protocol` kullanmalıdır.

Concrete kaynak sınıflarının zorunlu olarak bu arayüzden kalıtım alması
gerekmemelidir. Gerekli alanları ve metotları sağlamaları yeterli olmalıdır.

### Advisory Source Bilgisi

Her vulnerability source aşağıdaki property değerini sağlamalıdır:

```python
advisory_source
```

Bu property bir `AdvisorySource` modeli döndürmelidir.

Örnek:

```python
source.advisory_source == AdvisorySource(
    name="OSV",
    url="https://osv.dev",
)
```

Bu bilgi:

- Kaynak adını kullanıcıya göstermek
- Bulguların hangi kaynaktan geldiğini belirtmek
- Terminal ve JSON raporlarına kaynak bilgisi eklemek

için kullanılabilecektir.

Property aynı kaynak örneği için deterministik davranmalıdır.

### Vulnerability Sorgulama Metodu

Her kaynak aşağıdaki metodu sağlamalıdır:

```python
find_vulnerabilities(
    dependency: Dependency,
) -> tuple[DependencyFinding, ...]
```

Metot tek bir `Dependency` almalı ve bu dependency değerini etkileyen
vulnerability bulgularını tuple olarak döndürmelidir.

Bulgu yoksa:

```python
()
```

döndürülmelidir.

Bulgu bulunduğunda:

```python
(
    DependencyFinding(...),
    DependencyFinding(...),
)
```

biçiminde sonuç üretilmelidir.

`None`, liste veya generator public dönüş değeri olarak kullanılmamalıdır.

### Dependency Bilgisinin Korunması

Kaynağa verilen `Dependency` modeli değiştirilmemelidir.

Concrete kaynak, dış servise sorgu hazırlarken paket adını normalize edebilir:

```python
normalized_name = normalize_package_name(
    dependency.name
)
```

Ancak döndürülen `DependencyFinding.dependency` alanında kullanıcının orijinal
dependency modeli korunmalıdır.

Örnek:

```python
dependency.name == "Sample_Package"
normalized_query_name == "sample-package"
finding.dependency is dependency
```

Interface kendi başına paket adı normalizasyonu yapmamalıdır. Bu işlem concrete
kaynak uygulamasının sorgu hazırlama sorumluluğudur.

### Bulgu Sözleşmesi

Döndürülen her değer `DependencyFinding` örneği olmalıdır.

Her bulgu:

- Sorgulanan dependency bilgisini içermelidir.
- Advisory kimliğini içermelidir.
- Kullanıcı tarafından okunabilir açıklama içermelidir.
- Kaynak bilgisini içermelidir.
- Biliniyorsa severity bilgisini içermelidir.
- Biliniyorsa fixed version bilgisini içermelidir.
- Biliniyorsa CVE veya GHSA alias değerlerini içermelidir.

Concrete kaynaklar, eksik severity bilgisinde:

```python
VulnerabilitySeverity.UNKNOWN
```

değerini kullanmalıdır.

Eksik fixed version değeri:

```python
None
```

olmalıdır.

Eksik aliases değeri:

```python
()
```

olmalıdır.

### Sonuç Sırası

Concrete kaynak aynı advisory verileri için deterministik sonuç sırası
üretmelidir.

Arayüz katmanı:

- Bulguları alfabetik olarak sıralamamalıdır.
- Duplicate advisory kayıtlarını otomatik kaldırmamalıdır.
- Severity değerine göre yeniden sıralama yapmamalıdır.
- Kaynaktan gelen bulguları gizlememelidir.

Sıralama ve duplicate politikası gerekiyorsa daha üst bir tarama katmanında
ayrıca tanımlanmalıdır.

### Hata Davranışı

Vulnerability source interface hata yakalamamalı veya dönüştürmemelidir.

Concrete kaynaklarda oluşabilecek hata örnekleri:

- Ağ bağlantısı hatası
- Zaman aşımı
- HTTP hata cevabı
- Geçersiz JSON
- Beklenmeyen API cevabı
- Eksik advisory alanları

Bu hataların nasıl temsil edileceği concrete istemci geliştirmesinde ayrıca
tanımlanacaktır.

Interface bu aşamada:

- Retry uygulamayacaktır.
- Timeout değeri belirlemeyecektir.
- Hataları boş bulgu sonucu gibi göstermeyecektir.
- Hataları terminale yazmayacaktır.
- Exit code hesaplamayacaktır.

### Sahte Kaynak Kullanımı

Unit testlerde internet bağlantısı kullanılmamalıdır.

Testlerde aşağıdaki gibi basit bir fake kaynak oluşturulabilmelidir:

```python
class FakeVulnerabilitySource:
    def __init__(
        self,
        findings: tuple[DependencyFinding, ...],
    ) -> None:
        self._findings = findings
        self.received_dependencies: list[
            Dependency
        ] = []

    @property
    def advisory_source(self) -> AdvisorySource:
        return AdvisorySource(
            name="Fake",
            url=None,
        )

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        self.received_dependencies.append(
            dependency
        )
        return self._findings
```

Fake sınıfın arayüzü yapısal olarak karşılaması yeterli olmalıdır.

### Runtime Davranışı

Arayüz mümkünse:

```python
@runtime_checkable
```

ile tanımlanmalıdır.

Böylece testlerde ve dependency injection sınırlarında aşağıdaki kontrol
yapılabilecektir:

```python
isinstance(
    fake_source,
    VulnerabilitySource,
)
```

Runtime kontrolü yalnızca gerekli property ve metotların varlığını doğrular.

Metotların gerçek dönüş değerleri ayrıca unit testlerle doğrulanmalıdır.

### Paket Exportu

Aşağıdaki import çalışmalıdır:

```python
from dependency_scanner import VulnerabilitySource
```

Mevcut exportlar korunmalıdır:

- Dependency modelleri
- Requirements parser bileşenleri
- Paket adı normalizasyon fonksiyonu

### Sorumluluk Sınırları

Vulnerability source interface:

- Requirements dosyası okumayacaktır.
- Requirements satırı ayrıştırmayacaktır.
- Dependency modelini değiştirmeyecektir.
- Paket adı normalizasyonunu kendisi uygulamayacaktır.
- Paket sürümü karşılaştırmayacaktır.
- HTTP isteği göndermeyecektir.
- OSV cevabı ayrıştırmayacaktır.
- Retry veya timeout politikası uygulamayacaktır.
- Cache kullanmayacaktır.
- Terminal raporu üretmeyecektir.
- JSON dosyası yazmayacaktır.
- Exit code hesaplamayacaktır.
- Static analyzer paketine bağımlı olmayacaktır.

### Test Gereksinimleri

Unit testler en az aşağıdaki davranışları doğrulamalıdır:

- Public `VulnerabilitySource` importu
- Protocol tanımının runtime kontrolüne uygun olması
- Fake kaynağın arayüzü karşılaması
- Eksik property içeren nesnenin arayüzü karşılamaması
- Eksik metot içeren nesnenin arayüzü karşılamaması
- `advisory_source` property değerinin `AdvisorySource` olması
- `find_vulnerabilities()` metodunun dependency alması
- Sorgulanan dependency örneğinin korunması
- Bulgusuz sonucun boş tuple olması
- Tek bulgulu sonucun tuple olması
- Birden fazla bulgunun kaynak sırasının korunması
- Döndürülen değerlerin `DependencyFinding` olması
- Dependency modelinin değiştirilmemesi
- Fake kaynağın internet bağlantısı kullanmaması
- Mevcut public package exportlarının korunması
- Static analyzer paketinden bağımsızlık
- Bütün mevcut testlerin geçmeye devam etmesi
- Self-analysis sonucunun temiz olması

### Kabul Kriterleri

1. `vulnerability_source.py` modülü oluşturulmalıdır.
2. `VulnerabilitySource` protocol arayüzü tanımlanmalıdır.
3. Arayüz `advisory_source` property değerini tanımlamalıdır.
4. Arayüz `find_vulnerabilities()` metodunu tanımlamalıdır.
5. Metot tuple biçiminde `DependencyFinding` sonuçları üretmelidir.
6. Bulgusuz durumda boş tuple kullanılmalıdır.
7. Runtime protocol kontrolü desteklenmelidir.
8. Fake kaynak sınıfı internet olmadan test edilebilmelidir.
9. Public interface paket seviyesinden export edilmelidir.
10. Mevcut modeller, parser ve normalizer davranışları korunmalıdır.
11. Arayüz gerçek HTTP veya OSV kodu içermemelidir.
12. Unit testler dış servislere bağlanmamalıdır.
13. Bütün proje testleri geçmelidir.
14. SecureCode Analyzer self-analysis sonucu temiz olmalıdır.

### Planlanan Git Commitleri

```text
docs(dependency-scanner): define vulnerability source requirements
feat(dependency-scanner): add vulnerability source interface
docs(dependency-scanner): document vulnerability source interface
```
## Gerçekleştirilen Vulnerability Source Interface

Dependency scanner’ın farklı güvenlik açığı kaynaklarıyla çalışabilmesi için
ortak bir protocol arayüzü uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/vulnerability_source.py
tests/test_vulnerability_source.py
```

Public paket export dosyası güncellenmiştir:

```text
src/dependency_scanner/__init__.py
```

### Public Protocol

Aşağıdaki protocol paket seviyesinden dışa aktarılmaktadır:

```python
from dependency_scanner import VulnerabilitySource
```

Protocol tanımı:

```python
@runtime_checkable
class VulnerabilitySource(Protocol):
    @property
    def advisory_source(self) -> AdvisorySource:
        ...

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        ...
```

### Advisory Source Bilgisi

Her uyumlu kaynak bir `AdvisorySource` modeli sağlamaktadır.

Bu model:

- Kaynağın adını
- Opsiyonel kaynak bağlantısını

temsil eder.

Örnek:

```python
AdvisorySource(
    name="Fake",
    url=None,
)
```

### Vulnerability Sorgusu

`find_vulnerabilities()` tek bir `Dependency` alır.

Dönüş değeri:

```python
tuple[DependencyFinding, ...]
```

olmalıdır.

Bulgu bulunmadığında:

```python
()
```

döndürülür.

Bir veya daha fazla bulgu bulunduğunda sonuçların tuple sırası korunur.

### Yapısal Protocol Davranışı

Protocol yapısal uyumluluk kullanmaktadır.

Bir sınıfın doğrudan `VulnerabilitySource` değerinden kalıtım alması
gerekmez.

Aşağıdaki bileşenleri sağlaması yeterlidir:

- `advisory_source` property
- `find_vulnerabilities()` metodu

Runtime kontrolü:

```python
isinstance(
    source,
    VulnerabilitySource,
)
```

ile yapılabilir.

Eksik property veya metot bulunan nesneler protocol kontrolünü geçmez.

### Dependency Koruması

Testlerde sorgulanan dependency örneğinin aynı nesne olarak kaynağa
iletildiği doğrulanmıştır.

Fake kaynak:

- Dependency modelini değiştirmez.
- Paket adını otomatik normalize etmez.
- Yeni bir dependency modeli oluşturmaz.
- Döndürülen bulgularda orijinal dependency örneğini koruyabilir.

### Deterministik Fake Kaynak

Unit testlerde internet gerektirmeyen fake kaynak kullanılmıştır.

Fake kaynak:

1. Aldığı dependency örneğini kaydeder.
2. Önceden yapılandırılmış bulguları döndürür.
3. Bulgusuz durumda boş tuple döndürür.
4. Birden fazla bulgunun sırasını değiştirmez.
5. Dependency modelinin mevcut alanlarını korur.

### Sorumluluk Sınırları

Vulnerability source interface:

- Requirements dosyası okumaz.
- Requirements satırı ayrıştırmaz.
- Paket adı normalizasyonu yapmaz.
- Dependency modelini değiştirmez.
- HTTP isteği göndermez.
- OSV cevabı ayrıştırmaz.
- Retry, timeout veya cache politikası uygulamaz.
- Hataları boş bulgu sonucuna dönüştürmez.
- Terminal veya JSON raporu üretmez.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

Vulnerability source testleri:

```text
10 passed
```

Tam test paketi:

```text
414 passed
```

Derleme doğrulaması:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
```

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```
## OSV Response Model Gereksinimleri

### Amaç

OSV response modelleri, OSV API tarafından döndürülen vulnerability
bilgilerini uygulama içinde immutable ve tip güvenli Python nesneleriyle
temsil edecektir.

Bu modeller sayesinde:

- OSV JSON ayrıştırma işlemi model yapısından ayrılacaktır.
- Vulnerability kayıtları deterministik biçimde taşınabilecektir.
- Unit testlerde gerçek ağ bağlantısı kullanılmayacaktır.
- OSV istemcisi ile DependencyFinding dönüştürücüsü birbirinden
  ayrılabilecektir.
- Eksik veya opsiyonel OSV alanları açık biçimde temsil edilebilecektir.

Planlanan modül:

```text
src/dependency_scanner/osv_models.py
```

Planlanan test dosyası:

```text
tests/test_osv_models.py
```

### Model Listesi

Aşağıdaki modeller planlanmaktadır:

```text
OsvSeverity
OsvRangeEvent
OsvRange
OsvPackage
OsvAffectedPackage
OsvVulnerability
OsvQueryResponse
```

Model sınıfları:

- `dataclass` kullanmalıdır.
- `frozen=True` olmalıdır.
- `slots=True` olmalıdır.
- Mutable liste yerine tuple kullanmalıdır.
- JSON-serializable sözlük çıktısı üretebilmelidir.
- Ağ veya dosya işlemi yapmamalıdır.

### OsvSeverity

OSV severity kaydını temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvSeverity:
    severity_type: str
    score: str
```

`severity_type` örnekleri:

```text
CVSS_V2
CVSS_V3
CVSS_V4
```

`score`, OSV tarafından sağlanan severity veya CVSS değerini orijinal string
biçiminde korumalıdır.

Bu model kendi başına severity sınıflandırması yapmamalıdır.

### OsvRangeEvent

Vulnerable version range içindeki bir olayı temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvRangeEvent:
    introduced: str | None = None
    fixed: str | None = None
    last_affected: str | None = None
    limit: str | None = None
```

Bir event aşağıdaki bilgilerden birini veya gerekli olduğu durumda uygun
kombinasyonunu taşıyabilir:

- Vulnerability başlangıcı
- Düzeltilen sürüm
- Etkilenen son sürüm
- Range sınırı

Eksik alanlar `None` olmalıdır.

### OsvRange

Bir affected package içindeki version range bilgisini temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvRange:
    range_type: str
    events: tuple[OsvRangeEvent, ...]
```

`range_type` örnekleri:

```text
ECOSYSTEM
SEMVER
GIT
```

Event sırası OSV cevabındaki sırayla korunmalıdır.

Model:

- Event sırasını değiştirmemelidir.
- Version karşılaştırması yapmamalıdır.
- Vulnerable olup olmadığına karar vermemelidir.

### OsvPackage

OSV affected kaydındaki paket bilgisini temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvPackage:
    ecosystem: str
    name: str
```

Python dependency sorguları için ecosystem değeri genellikle:

```text
PyPI
```

olacaktır.

Paket adı OSV cevabındaki biçimiyle korunmalıdır. Bu model otomatik paket adı
normalizasyonu yapmamalıdır.

### OsvAffectedPackage

Bir vulnerability tarafından etkilenen paket bilgisini temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvAffectedPackage:
    package: OsvPackage
    ranges: tuple[OsvRange, ...] = ()
    versions: tuple[str, ...] = ()
    severity: tuple[OsvSeverity, ...] = ()
```

Model aşağıdaki bilgileri taşıyabilmelidir:

- Etkilenen paket
- Vulnerable version range değerleri
- Açıkça listelenmiş affected sürümler
- Pakete özel severity değerleri

Collection alanları tuple olmalıdır.

OSV cevabında alan bulunmuyorsa boş tuple kullanılmalıdır.

### OsvVulnerability

Tek bir OSV vulnerability kaydını temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvVulnerability:
    advisory_id: str
    summary: str | None = None
    details: str | None = None
    aliases: tuple[str, ...] = ()
    severity: tuple[OsvSeverity, ...] = ()
    affected: tuple[OsvAffectedPackage, ...] = ()
```

`advisory_id` OSV kaydının zorunlu kimliğidir.

Örnekler:

```text
GHSA-xxxx-xxxx-xxxx
PYSEC-2024-000
CVE-2024-0000
```

`summary` veya `details` bulunmuyorsa `None` kullanılmalıdır.

Aliases sırası değiştirilmemelidir.

Aliases içinde aşağıdaki kimlik türleri bulunabilir:

```text
CVE
GHSA
PYSEC
```

Model duplicate alias değerlerini otomatik kaldırmamalıdır.

### OsvQueryResponse

Tek bir OSV query cevabını temsil etmelidir.

Planlanan alanlar:

```python
@dataclass(frozen=True, slots=True)
class OsvQueryResponse:
    vulnerabilities: tuple[OsvVulnerability, ...] = ()
    next_page_token: str | None = None
```

OSV JSON cevabındaki:

```text
vulns
```

alanı parser katmanında:

```text
vulnerabilities
```

alanına dönüştürülecektir.

Bulgu bulunmadığında:

```python
OsvQueryResponse(
    vulnerabilities=(),
    next_page_token=None,
)
```

oluşturulabilmelidir.

Pagination token bulunmuyorsa `None` kullanılmalıdır.

Vulnerability sırası OSV cevabındaki sırayla korunmalıdır.

### Immutable Davranış

Bütün modeller immutable olmalıdır.

Aşağıdaki gibi alan değişikliği yapılamamalıdır:

```python
vulnerability.advisory_id = "CHANGED"
```

Tuple alanlarına yeni değer eklenememelidir.

Immutable yapı:

- Testlerin deterministik olmasını
- API cevabının yanlışlıkla değiştirilmemesini
- Katmanlar arasında güvenilir veri aktarımını

sağlayacaktır.

### Sözlük Dönüşümü

Her model JSON-serializable sözlük çıktısı sağlayabilmelidir:

```python
model.to_dict()
```

Nested modeller recursive olarak sözlüğe dönüştürülmelidir.

Tuple alanları JSON çıktısına uygun biçimde listeye dönüştürülebilir.

`None` değerleri korunmalıdır.

Enum kullanılmadığı için ham OSV değerleri string olarak korunmalıdır.

### Doğrulama Kuralları

Aşağıdaki zorunlu string alanları boş olmamalıdır:

```text
OsvSeverity.severity_type
OsvSeverity.score
OsvRange.range_type
OsvPackage.ecosystem
OsvPackage.name
OsvVulnerability.advisory_id
```

Aşağıdaki girdiler reddedilmelidir:

- String olmayan zorunlu alan
- Boş string
- Whitespace-only string
- Collection alanında yanlış model tipi
- Collection yerine string, liste veya dictionary verilmesi

Geçersiz girdilerde:

```python
ValueError
```

üretilmelidir.

Opsiyonel string alanlar:

```text
summary
details
next_page_token
introduced
fixed
last_affected
limit
```

için `None` kabul edilmelidir.

String sağlandığında boş veya whitespace-only değer kabul edilmemelidir.

### Sıra Koruması

Aşağıdaki koleksiyonların sırası değiştirilmemelidir:

- Severity kayıtları
- Range event kayıtları
- Range kayıtları
- Explicit affected versions
- Aliases
- Affected package kayıtları
- Vulnerability kayıtları

Modeller:

- Alfabetik sıralama yapmamalıdır.
- Duplicate değerleri otomatik kaldırmamalıdır.
- Severity değerine göre sıralama yapmamalıdır.

### Public Paket Exportu

Aşağıdaki importlar çalışmalıdır:

```python
from dependency_scanner import (
    OsvAffectedPackage,
    OsvPackage,
    OsvQueryResponse,
    OsvRange,
    OsvRangeEvent,
    OsvSeverity,
    OsvVulnerability,
)
```

Mevcut public exportlar korunmalıdır:

- Dependency modelleri
- Requirements parser
- Package name normalizer
- VulnerabilitySource protocol

### Sorumluluk Sınırları

OSV response modelleri:

- HTTP isteği göndermeyecektir.
- OSV API bağlantısı kurmayacaktır.
- JSON metni ayrıştırmayacaktır.
- Dependency modeli oluşturmayacaktır.
- Paket adı normalizasyonu yapmayacaktır.
- Version karşılaştırması yapmayacaktır.
- Bir sürümün vulnerable olup olmadığına karar vermeyecektir.
- OSV severity değerini uygulama severity enumuna dönüştürmeyecektir.
- DependencyFinding oluşturmayacaktır.
- Retry, timeout veya cache uygulamayacaktır.
- Terminal raporu üretmeyecektir.
- JSON dosyası yazmayacaktır.
- Exit code hesaplamayacaktır.
- Static analyzer paketine bağımlı olmayacaktır.

### Test Gereksinimleri

Unit testler en az aşağıdaki davranışları doğrulamalıdır:

- Bütün OSV modellerinin public importu
- Zorunlu alanlarla model oluşturma
- Opsiyonel alanların varsayılan değerleri
- Nested model oluşturma
- Empty query response
- Birden fazla vulnerability sırasının korunması
- Alias sırasının korunması
- Affected package sırasının korunması
- Version sırasının korunması
- Range event sırasının korunması
- Severity sırasının korunması
- Pagination token desteği
- Immutable model davranışı
- Recursive `to_dict()` çıktısı
- Boş zorunlu stringlerin reddedilmesi
- Whitespace-only değerlerin reddedilmesi
- Yanlış collection tiplerinin reddedilmesi
- Collection içindeki yanlış model tiplerinin reddedilmesi
- Modellerin internet bağlantısı kullanmaması
- Mevcut public exportların korunması
- Bütün mevcut testlerin geçmesi
- Self-analysis sonucunun temiz olması

### Kabul Kriterleri

1. `osv_models.py` oluşturulmalıdır.
2. Yedi OSV response modeli tanımlanmalıdır.
3. Modeller frozen ve slotted dataclass olmalıdır.
4. Collection alanları tuple olmalıdır.
5. Opsiyonel alanlar `None` ile temsil edilmelidir.
6. Nested response yapısı desteklenmelidir.
7. OSV cevabındaki sıra korunmalıdır.
8. Modeller recursive sözlük çıktısı üretmelidir.
9. Zorunlu alanlar doğrulanmalıdır.
10. Public package exportları eklenmelidir.
11. Gerçek HTTP veya JSON parser kodu eklenmemelidir.
12. Unit testler dış servislere bağlanmamalıdır.
13. Mevcut testler geçmeye devam etmelidir.
14. SecureCode Analyzer self-analysis sonucu temiz olmalıdır.

### Planlanan Git Commitleri

```text
docs(dependency-scanner): define OSV response model requirements
feat(dependency-scanner): add OSV response models
docs(dependency-scanner): document OSV response models
```
## Gerçekleştirilen OSV Response Modelleri

OSV API cevaplarını uygulama içinde immutable ve tip güvenli biçimde temsil
etmek için response modelleri uygulanmıştır.

### Oluşturulan Dosyalar

```text
src/dependency_scanner/osv_models.py
tests/test_osv_models.py
```

Public paket export dosyası güncellenmiştir:

```text
src/dependency_scanner/__init__.py
```

### Uygulanan Modeller

```text
OsvSeverity
OsvRangeEvent
OsvRange
OsvPackage
OsvAffectedPackage
OsvVulnerability
OsvQueryResponse
```

### OsvSeverity

OSV severity kaydını temsil eder:

```python
OsvSeverity(
    severity_type="CVSS_V3",
    score="CVSS:3.1/AV:N/AC:L",
)
```

Model severity türünü ve score değerini orijinal string biçiminde korur.

Severity sınıflandırması veya CVSS hesaplaması yapmaz.

### OsvRangeEvent

Version range içindeki olayları temsil eder:

```python
OsvRangeEvent(
    introduced="0",
)

OsvRangeEvent(
    fixed="2.0.0",
)
```

Desteklenen alanlar:

```text
introduced
fixed
last_affected
limit
```

Eksik alanlar `None` olarak korunur.

### OsvRange

Affected version range bilgisini temsil eder:

```python
OsvRange(
    range_type="ECOSYSTEM",
    events=(
        OsvRangeEvent(
            introduced="0",
        ),
        OsvRangeEvent(
            fixed="2.0.0",
        ),
    ),
)
```

Event sırası değişmeden korunur.

Model kendi başına sürüm karşılaştırması yapmaz.

### OsvPackage

OSV paket bilgisini temsil eder:

```python
OsvPackage(
    ecosystem="PyPI",
    name="sample-package",
)
```

Paket adı OSV cevabındaki biçimiyle korunur.

Otomatik paket adı normalizasyonu yapılmaz.

### OsvAffectedPackage

Bir advisory tarafından etkilenen paket bilgisini temsil eder:

```python
OsvAffectedPackage(
    package=OsvPackage(
        ecosystem="PyPI",
        name="sample-package",
    ),
    ranges=(),
    versions=(),
    severity=(),
)
```

Collection alanları tuple kullanır.

Eksik collection değerleri boş tuple olarak temsil edilir.

### OsvVulnerability

Tek bir OSV vulnerability kaydını temsil eder:

```python
OsvVulnerability(
    advisory_id="PYSEC-2026-1",
    summary="Example vulnerability",
    aliases=(
        "CVE-2026-0001",
        "GHSA-xxxx-yyyy-zzzz",
    ),
)
```

Desteklenen alanlar:

```text
advisory_id
summary
details
aliases
severity
affected
```

Alias sırası korunur ve duplicate değerler otomatik kaldırılmaz.

### OsvQueryResponse

Bir OSV query cevabını temsil eder:

```python
OsvQueryResponse(
    vulnerabilities=(),
    next_page_token=None,
)
```

Bulgu bulunmadığında boş vulnerability tuple değeri kullanılır.

Pagination token bulunmadığında `None` kullanılır.

### Immutable Model Yapısı

Bütün modeller:

```python
@dataclass(
    frozen=True,
    slots=True,
)
```

yapısını kullanır.

Model alanlarının sonradan değiştirilmesi mümkün değildir.

Bu davranış unit testlerde `FrozenInstanceError` ile doğrulanmıştır.

### Recursive Sözlük Dönüşümü

Bütün modeller ortak olarak:

```python
model.to_dict()
```

metodunu sağlar.

Dönüşüm sırasında:

- Nested dataclass modeller dictionary değerine dönüştürülür.
- Tuple değerleri listeye dönüştürülür.
- `None` değerleri korunur.
- String değerleri değiştirilmez.
- Sonuç `json.dumps()` ile serialize edilebilir.

### Veri Doğrulaması

Zorunlu string alanlar:

```text
severity_type
score
range_type
ecosystem
name
advisory_id
```

aşağıdaki değerleri kabul etmez:

- String olmayan değer
- Boş string
- Whitespace-only string

Opsiyonel string alanlar `None` kabul eder.

String sağlandığında boş veya whitespace-only değer reddedilir.

Collection alanları:

- Tuple olmak zorundadır.
- Liste kabul etmez.
- String kabul etmez.
- Dictionary kabul etmez.
- İçindeki değerler beklenen model veya string türünde olmalıdır.

Geçersiz değerlerde `ValueError` üretilir.

### Sıra Koruması

Aşağıdaki collection değerlerinin sırası korunur:

- Query içindeki vulnerability kayıtları
- Vulnerability aliases değerleri
- Affected package kayıtları
- Explicit version değerleri
- Range kayıtları
- Range event kayıtları
- Severity kayıtları

Modeller sıralama veya duplicate temizleme uygulamaz.

### Sorumluluk Sınırları

OSV response modelleri:

- HTTP isteği göndermez.
- OSV API istemcisi oluşturmaz.
- JSON metni ayrıştırmaz.
- Dependency modeli oluşturmaz.
- Paket adı normalizasyonu yapmaz.
- Sürüm karşılaştırması yapmaz.
- Bir sürümün vulnerable olduğuna karar vermez.
- Severity dönüşümü yapmaz.
- Dependency finding oluşturmaz.
- Retry, timeout veya cache uygulamaz.
- Terminal çıktısı üretmez.
- JSON dosyası yazmaz.
- Exit code hesaplamaz.
- Static analyzer paketine bağımlı değildir.

### Test Sonuçları

OSV response model testleri:

```text
74 passed
```

Tam test paketi:

```text
488 passed
```

Derleme doğrulaması:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
```

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
``
## OSV Response Parser Gereksinimleri

OSV API tarafından döndürülen ve daha önce JSON formatından Python
nesnelerine dönüştürülmüş veriler, dependency scanner içindeki immutable OSV
response modellerine çevrilecektir.

### Planlanan Dosyalar

```text
src/dependency_scanner/osv_parser.py
tests/test_osv_parser.py
```

Public paket export dosyası:

```text
src/dependency_scanner/__init__.py
```

güncellenecektir.

### Public API

Parser katmanı aşağıdaki public bileşenleri sağlayacaktır:

```python
from dependency_scanner import (
    OsvResponseParseError,
    parse_osv_query_response,
)
```

Ana parser fonksiyonu:

```python
parse_osv_query_response(
    payload: object,
) -> OsvQueryResponse
```

şeklinde çalışacaktır.

### Girdi Sınırı

Parser doğrudan JSON metni kabul etmeyecektir.

Girdi, `json.loads()` veya bir HTTP istemcisi tarafından daha önce Python
nesnelerine dönüştürülmüş bir payload olacaktır.

Örnek:

```python
payload = {
    "vulns": [
        {
            "id": "PYSEC-2026-1",
            "summary": "Example vulnerability",
        },
    ],
}
```

### Top-Level Response

Top-level payload dictionary olmak zorundadır.

Desteklenen alanlar:

```text
vulns
next_page_token
```

`vulns` alanı bulunmadığında boş vulnerability collection kullanılacaktır.

`next_page_token` alanı bulunmadığında `None` kullanılacaktır.

### Vulnerability Dönüşümü

Her vulnerability kaydı:

```text
OsvVulnerability
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
id
summary
details
aliases
severity
affected
```

OSV cevabındaki:

```text
id
```

alanı model içindeki:

```text
advisory_id
```

alanına aktarılacaktır.

`id` zorunlu ve boş olmayan bir string olmalıdır.

### Severity Dönüşümü

Severity kayıtları:

```text
OsvSeverity
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
type
score
```

OSV cevabındaki `type` alanı model içindeki `severity_type` alanına
aktarılacaktır.

### Affected Package Dönüşümü

Affected kayıtları:

```text
OsvAffectedPackage
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
package
ranges
versions
severity
```

`package` alanı zorunlu olacaktır.

### Package Dönüşümü

Package kayıtları:

```text
OsvPackage
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
ecosystem
name
```

Her iki alan da zorunlu ve boş olmayan string olmalıdır.

### Range Dönüşümü

Range kayıtları:

```text
OsvRange
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
type
events
```

OSV cevabındaki `type` alanı model içindeki `range_type` alanına
aktarılacaktır.

### Range Event Dönüşümü

Range event kayıtları:

```text
OsvRangeEvent
```

modeline dönüştürülecektir.

Desteklenen alanlar:

```text
introduced
fixed
last_affected
limit
```

Eksik event alanları `None` olarak korunacaktır.

### Collection Dönüşümü

OSV payload içindeki listeler model katmanında tuple değerlerine
dönüştürülecektir.

Dönüştürülecek collection alanları:

```text
vulns
aliases
severity
affected
ranges
events
versions
```

Collection sırası korunacaktır.

Duplicate değerler kaldırılmayacaktır.

### Eksik Opsiyonel Alanlar

Eksik opsiyonel string alanları `None` olarak temsil edilecektir.

Eksik opsiyonel collection alanları boş tuple olarak temsil edilecektir.

Parser eksik opsiyonel alanlar nedeniyle hata üretmeyecektir.

### Bilinmeyen Alanlar

OSV payload içindeki parser tarafından desteklenmeyen ek alanlar
yok sayılacaktır.

Bu davranış OSV cevabına ileride yeni alanlar eklenmesi durumunda parser
uyumluluğunun korunmasını sağlayacaktır.

### Hata Yönetimi

Geçersiz response verilerinde:

```python
OsvResponseParseError
```

üretilecektir.

Hata mesajı mümkün olduğunda geçersiz alanın konumunu içerecektir.

Örnek konumlar:

```text
payload
vulns
vulns[0]
vulns[0].id
vulns[0].affected[0].package
vulns[0].affected[0].ranges[0].events
```

Aşağıdaki durumlar parse hatası olacaktır:

- Top-level payload değerinin dictionary olmaması
- Collection alanının liste olmaması
- Collection içindeki elemanın dictionary olmaması
- Zorunlu alanın eksik olması
- String alanının yanlış türde olması
- Zorunlu string alanının boş olması
- Collection içindeki string değerinin yanlış türde olması
- Nested package veya range kaydının geçersiz olması

Alt model tarafından üretilen doğrulama hataları parser hata türüne
dönüştürülecektir.

### Sıra Koruması

Parser aşağıdaki alanların orijinal sırasını koruyacaktır:

- Vulnerability kayıtları
- Alias kayıtları
- Severity kayıtları
- Affected package kayıtları
- Range kayıtları
- Range event kayıtları
- Explicit version kayıtları

Parser otomatik sıralama veya duplicate temizleme yapmayacaktır.

### Sorumluluk Sınırları

OSV response parser:

- HTTP isteği göndermez.
- OSV API bağlantısı kurmaz.
- JSON metninde `json.loads()` çalıştırmaz.
- Dosya okumaz veya yazmaz.
- Paket adını normalize etmez.
- Paket sürümü karşılaştırmaz.
- Bir sürümün vulnerable olduğuna karar vermez.
- Severity seviyesini dönüştürmez.
- `Dependency` modeli oluşturmaz.
- `DependencyFinding` oluşturmaz.
- Retry, timeout veya cache uygulamaz.
- Terminal çıktısı üretmez.
- JSON raporu oluşturmaz.
- Exit code hesaplamaz.

### Test Gereksinimleri

Unit testler en az aşağıdaki durumları kapsayacaktır:

- Boş response payload
- Tek vulnerability kaydı
- Tam nested vulnerability kaydı
- Pagination token
- Eksik opsiyonel alanlar
- Bilinmeyen alanların yok sayılması
- Collection sırasının korunması
- Duplicate değerlerin korunması
- Listelerin tuple değerlerine dönüştürülmesi
- Geçersiz top-level payload
- Geçersiz vulnerability kaydı
- Eksik vulnerability ID değeri
- Geçersiz alias collection
- Geçersiz severity kaydı
- Geçersiz affected package
- Geçersiz package kaydı
- Geçersiz range kaydı
- Geçersiz range event kaydı
- Geçersiz version collection
- Model doğrulama hatalarının parser hatasına dönüştürülmesi

Testler tamamen offline çalışacaktır.

HTTP bağlantısı veya gerçek OSV servisi kullanılmayacaktır.

## Navigation

- [Dependency Scanner sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)