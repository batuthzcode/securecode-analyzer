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

## Navigation

- [Dependency Scanner sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)