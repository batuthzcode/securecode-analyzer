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
## Uygulanan Vulnerability Source Interface

Dependency scanner bileşenine güvenlik açığı kaynakları için ortak bir
arayüz eklenmiştir.

Oluşturulan modül:

```text
src/dependency_scanner/vulnerability_source.py
```

Test dosyası:

```text
tests/test_vulnerability_source.py
```

### Public API

Arayüz paket seviyesinden import edilebilir:

```python
from dependency_scanner import VulnerabilitySource
```

### Protocol Sözleşmesi

`VulnerabilitySource`, `typing.Protocol` ve `@runtime_checkable` kullanır.

Her vulnerability source aşağıdaki property değerini sağlamalıdır:

```python
@property
def advisory_source(self) -> AdvisorySource:
    ...
```

Her kaynak ayrıca aşağıdaki sorgu metodunu sağlamalıdır:

```python
def find_vulnerabilities(
    self,
    dependency: Dependency,
) -> tuple[DependencyFinding, ...]:
    ...
```

Bulgu bulunmadığında boş tuple döndürülür:

```python
()
```

### Yapısal Uyumluluk

Concrete kaynak sınıflarının doğrudan `VulnerabilitySource` sınıfından
kalıtım alması gerekmez.

Gerekli property ve metodu sağlayan sınıflar yapısal olarak protocol
sözleşmesini karşılayabilir:

```python
isinstance(
    fake_source,
    VulnerabilitySource,
)
```

### Testlerde Fake Kaynak

Unit testlerde gerçek ağ bağlantısı yerine deterministik fake kaynak
kullanılmıştır.

Fake kaynak:

- Sorgulanan dependency örneğini kaydeder.
- Yapılandırılmış bulguları tuple olarak döndürür.
- Bulgusuz durumda boş tuple döndürür.
- Bulgu sırasını değiştirmez.
- Dependency modelini değiştirmez.
- İnternet bağlantısı kullanmaz.

### Sorumluluk Sınırları

Bu interface:

- HTTP isteği göndermez.
- OSV cevabı ayrıştırmaz.
- Paket adı normalizasyonu yapmaz.
- Dependency modelini değiştirmez.
- Retry veya timeout politikası uygulamaz.
- Hataları yakalayıp gizlemez.
- Terminal veya JSON raporu üretmez.
- Exit code hesaplamaz.

Gerçek OSV istemcisi sonraki geliştirme aşamasında bu sözleşmeye uygun
olarak uygulanacaktır.

### Test Sonuçları

Vulnerability source testleri:

```text
10 passed
```

Tam proje testleri:

```text
414 passed
```

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```
## Uygulanan OSV Response Modelleri

Dependency scanner bileşenine OSV API cevaplarını immutable ve tip güvenli
Python nesneleriyle temsil eden response modelleri eklenmiştir.

Oluşturulan modül:

```text
src/dependency_scanner/osv_models.py
```

Test dosyası:

```text
tests/test_osv_models.py
```

### Public API

Aşağıdaki modeller paket seviyesinden import edilebilir:

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

### Model Yapısı

Uygulanan modeller:

```text
OsvSeverity
OsvRangeEvent
OsvRange
OsvPackage
OsvAffectedPackage
OsvVulnerability
OsvQueryResponse
```

Modeller:

- `dataclass` kullanır.
- `frozen=True` ile immutable davranır.
- `slots=True` kullanır.
- Collection alanlarında tuple kullanır.
- Nested modelleri destekler.
- JSON uyumlu sözlük çıktısı üretebilir.

### Nested Response Örneği

```python
response = OsvQueryResponse(
    vulnerabilities=(
        OsvVulnerability(
            advisory_id="PYSEC-2026-1",
            aliases=(
                "CVE-2026-0001",
            ),
            affected=(
                OsvAffectedPackage(
                    package=OsvPackage(
                        ecosystem="PyPI",
                        name="sample-package",
                    ),
                    ranges=(
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
                        ),
                    ),
                ),
            ),
        ),
    ),
)
```

### JSON Uyumlu Sözlük Çıktısı

Her model aşağıdaki metodu sağlar:

```python
data = response.to_dict()
```

Nested modeller recursive olarak dönüştürülür.

Tuple alanları JSON uyumlu listelere dönüştürülür:

```python
import json

serialized = json.dumps(
    response.to_dict()
)
```

### Veri Doğrulaması

Zorunlu string alanları boş veya whitespace-only değer kabul etmez.

Doğrulanan alanlardan bazıları:

```text
severity_type
score
range_type
ecosystem
name
advisory_id
```

Opsiyonel alanlar `None` kabul eder ancak boş string kabul etmez:

```text
introduced
fixed
last_affected
limit
summary
details
next_page_token
```

Collection alanlarının tuple olması gerekir.

Collection içindeki değerler de beklenen model veya string türüyle
eşleşmelidir.

Geçersiz girdilerde:

```python
ValueError
```

üretilir.

### Immutable Davranış

Model alanları oluşturulduktan sonra değiştirilemez:

```python
vulnerability.advisory_id = "CHANGED"
```

Bu işlem `FrozenInstanceError` üretir.

### Sıra Koruması

Modeller aşağıdaki değerlerin sırasını değiştirmez:

- Vulnerability kayıtları
- Alias değerleri
- Affected package kayıtları
- Version kayıtları
- Range kayıtları
- Range event kayıtları
- Severity kayıtları

Duplicate değerler otomatik kaldırılmaz ve alfabetik sıralama yapılmaz.

### Sorumluluk Sınırları

OSV response modelleri:

- HTTP isteği göndermez.
- OSV API bağlantısı kurmaz.
- JSON metni ayrıştırmaz.
- Paket adını normalize etmez.
- Sürüm karşılaştırması yapmaz.
- Vulnerable sürüm kararı vermez.
- `DependencyFinding` oluşturmaz.
- Retry, timeout veya cache uygulamaz.
- Terminal ya da JSON raporu üretmez.
- Exit code hesaplamaz.

### Test Sonuçları

OSV response model testleri:

```text
74 passed
```

Tam proje testleri:

```text
488 passed
```

Self-analysis:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```
## Uygulanan OSV Response Parser

Dependency scanner bileşenine, Python nesnelerine dönüştürülmüş OSV response
payload değerlerini immutable OSV modellerine çeviren parser katmanı
eklenmiştir.

Oluşturulan dosyalar:

```text
src/dependency_scanner/osv_parser.py
tests/test_osv_parser.py
```

### Public API

```python
from dependency_scanner import (
    OsvResponseParseError,
    parse_osv_query_response,
)
```

Örnek kullanım:

```python
payload = {
    "vulns": [
        {
            "id": "PYSEC-2026-1",
            "summary": "Example vulnerability",
        },
    ],
}

response = parse_osv_query_response(payload)
```

Parser bir:

```text
OsvQueryResponse
```

modeli döndürür.

### Desteklenen Dönüşümler

Desteklenen OSV alanları:

```text
vulns
id
summary
details
aliases
severity
affected
package
ranges
events
versions
next_page_token
```

Temel alan eşlemeleri:

```text
vulns → vulnerabilities
id → advisory_id
severity.type → severity_type
ranges.type → range_type
```

Payload içindeki listeler model katmanında tuple değerlerine dönüştürülür.

Parser:

- Eksik collection alanlarını boş tuple yapar.
- Eksik opsiyonel string alanlarını `None` yapar.
- Collection sırasını korur.
- Duplicate değerleri korur.
- Bilinmeyen alanları yok sayar.
- Nested response yapılarını ayrıştırır.
- Hatalı alanın konumunu hata mesajında gösterir.

Geçersiz payload değerlerinde:

```python
OsvResponseParseError
```

üretilir.

### Sorumluluk Sınırları

OSV response parser:

- HTTP isteği göndermez.
- OSV API bağlantısı kurmaz.
- JSON metninde `json.loads()` çalıştırmaz.
- Dosya işlemi yapmaz.
- Paket adını normalize etmez.
- Sürüm karşılaştırması yapmaz.
- Vulnerable sürüm kararı vermez.
- Dependency finding oluşturmaz.
- Retry, timeout veya cache uygulamaz.
- Terminal raporu veya exit code üretmez.

### Test Sonuçları

```text
OSV response parser tests: 76 passed
Complete test suite: 564 passed
Self-analysis: No findings found.
Exit code: 0
```

## Mevcut Durum
Dependency scanner geliştirmesi devam etmektedir. Ortak veri modelleri,
requirements parser, paket adı normalizasyonu, vulnerability source interface
ve OSV response modelleri tamamlanmıştır.

Sıradaki aşama OSV JSON cevaplarını response modellerine dönüştüren parser
katmanının geliştirilmesidir.
## Uygulanan Paket Adı Normalizasyonu

Dependency scanner bileşenine Python paket adlarını ortak bir biçime dönüştüren
normalizasyon fonksiyonu eklenmiştir.

Oluşturulan modül:

```text
src/dependency_scanner/package_normalizer.py
```

Test dosyası:

```text
tests/test_package_normalizer.py
```

### Public API

Normalizasyon fonksiyonu paket seviyesinden kullanılabilir:

```python
from dependency_scanner import normalize_package_name
```

Örnek:

```python
normalized_name = normalize_package_name(
    "Sample_Package"
)
```

Sonuç:

```text
sample-package
```

### Normalizasyon Kuralları

Fonksiyon:

1. Paket adının başındaki ve sonundaki whitespace değerlerini temizler.
2. Büyük harfleri küçük harfe dönüştürür.
3. Ardışık tire, alt çizgi ve nokta karakterlerini tek tireye dönüştürür.
4. Harf ve rakamları korur.

Örnekler:

| Girdi | Sonuç |
|---|---|
| `Flask` | `flask` |
| `Sample-Package` | `sample-package` |
| `sample_package` | `sample-package` |
| `sample.package` | `sample-package` |
| `sample---package` | `sample-package` |
| `sample-_.package` | `sample-package` |
| `Package2_Name` | `package2-name` |

Aşağıdaki yazımlar aynı normalize edilmiş değeri üretir:

```text
Sample-Package
sample_package
sample.package
sample---package
```

Ortak sonuç:

```text
sample-package
```

### Orijinal Dependency Bilgisinin Korunması

Normalizasyon fonksiyonu mevcut `Dependency` modelini değiştirmez.

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

Sonuç:

```text
dependency.name: Sample_Package
normalized_name: sample-package
```

Requirements parser paket adının orijinal yazımını korumaya devam eder.
Normalizasyon yalnızca açıkça çağrıldığında uygulanır.

### Girdi Doğrulaması

Aşağıdaki girdiler reddedilir:

- String olmayan değerler
- Boş string
- Yalnızca whitespace içeren değerler
- Yalnızca ayırıcı karakterlerden oluşan adlar
- Whitespace içeren paket adları
- Slash içeren paket adları
- `@`, `#` veya `:` gibi desteklenmeyen karakterler
- ASCII paket adı kapsamı dışındaki karakterler

Geçersiz girdiler:

```text
""
"   "
"-_."
"package name"
"package/name"
"package@name"
"package#name"
```

Bu durumlarda `ValueError` üretilir.

### Deterministik ve Idempotent Davranış

Aynı girdi her çağrıda aynı sonucu üretir.

Normalizasyon idempotent davranır:

```python
normalized_name = normalize_package_name(
    "Sample_Package"
)

assert normalize_package_name(
    normalized_name
) == normalized_name
```

### Sorumluluk Sınırları

Paket adı normalizasyonu:

- Requirements dosyası okumaz.
- Requirements satırı ayrıştırmaz.
- `Dependency` modelini değiştirmez.
- Paket sürümü karşılaştırmaz.
- Duplicate paket kontrolü yapmaz.
- OSV API isteği göndermez.
- Advisory kaydı ayrıştırmaz.
- Güvenlik açığı bulgusu oluşturmaz.
- Terminal veya JSON raporu üretmez.
- Exit code hesaplamaz.

### Test Sonuçları

Paket adı normalizasyon testleri:

```text
38 passed
```

Tam proje testleri:

```text
404 passed
```

SecureCode Analyzer self-analysis sonucu:

```text
No findings found.
```

Self-analysis exit code:

```text
0
```
## Uygulanan OSV Query Client

Dependency scanner bileşenine OSV servisine HTTP isteği gönderen query client
katmanı eklenmiştir.

### Public API

```python
from dependency_scanner import (
    OsvQueryClient,
    OsvQueryError,
)
```

Paket ve sürüm sorgusu:

```python
client = OsvQueryClient()

response = client.query_package(
    "jinja2",
    "3.1.4",
)
```

Kullanılan OSV endpoint:

```text
https://api.osv.dev/v1/query
```

HTTP metodu `POST`, ecosystem değeri `PyPI` olarak kullanılır.

Paket adı sorgudan önce mevcut `normalize_package_name()` fonksiyonuyla
normalize edilir.

Client varsayılan olarak:

```text
10 saniye
```

timeout kullanır.

Opsiyonel `page_token` desteği vardır. Client otomatik pagination yapmaz;
her çağrı tek bir OSV response sayfasını işler.

### Hata Yönetimi

Aşağıdaki durumlar `OsvQueryError` ile temsil edilir:

- HTTP hataları
- Network hataları
- Timeout
- Geçersiz JSON
- Geçersiz UTF-8
- Geçersiz OSV response
- Geçersiz package adı
- Geçersiz version
- Geçersiz page token
- Geçersiz timeout

OSV response verisi mevcut `parse_osv_query_response()` fonksiyonuyla
ayrıştırılır.

### Test Sonuçları

```text
OSV Query Client tests: 37 passed
Complete test suite: 601 passed
Self-analysis: No findings found.
Exit code: 0
```

## Uygulanan OSV Vulnerability Source

Dependency scanner bileşenine OSV query sonuçlarını ortak
`DependencyFinding` modellerine dönüştüren vulnerability source katmanı
eklenmiştir.

Oluşturulan dosyalar:

```text
src/dependency_scanner/osv_source.py
tests/test_osv_source.py
```

### Public API

```python
from dependency_scanner import (
    OsvVulnerabilitySource,
)
```

Örnek kullanım:

```python
source = OsvVulnerabilitySource()

findings = source.find_vulnerabilities(
    dependency
)
```

Source varsayılan olarak mevcut `OsvQueryClient` sınıfını kullanır. Unit
testlerde veya farklı çalışma ortamlarında uyumlu bir query client constructor
üzerinden verilebilir.

### Finding Dönüşümü

Her OSV vulnerability kaydı bir `DependencyFinding` değerine dönüştürülür.

Alan eşlemeleri:

```text
advisory_id → advisory_id
aliases → aliases
summary → message
ilk fixed range event → fixed_version
```

`summary` bulunmadığında `details` mesaj olarak kullanılır. Her ikisi de
bulunmadığında advisory ID içeren varsayılan bir mesaj oluşturulur.

Source bilgisi:

```python
AdvisorySource(
    name="OSV",
    url="https://osv.dev/",
)
```

Geçerli OSV `CVSS_V3` kayıtları artık CVSS v3 base score hesabıyla ortak
`VulnerabilitySeverity` değerlerine dönüştürülür. Desteklenmeyen veya geçersiz
severity kayıtlarında `VulnerabilitySeverity.UNKNOWN` kullanılır.

### Pagination ve Hata Yönetimi

Response içindeki `next_page_token` değeri kullanılarak bütün OSV sayfaları
sorgulanır. Sayfalardaki bulgular sıraları korunarak tek tuple içinde
birleştirilir.

`OsvQueryError` source katmanında gizlenmez veya başka bir hata türüne
dönüştürülmez; çağıran katmana aynen aktarılır.

Source katmanı:

- HTTP request oluşturmaz.
- JSON response ayrıştırmaz.
- Requirements dosyası okumaz.
- Paket adı normalize etmez.
- CVSS formülünü kendi içinde uygulamaz; ortak severity yardımcısını kullanır.
- Terminal çıktısı veya exit code üretmez.

### Test Sonuçları

```text
OSV Vulnerability Source tests: 14 passed
Complete test suite: 615 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Uygulanan OSV CVSS v3 Severity Mapping

Dependency scanner bileşenine OSV severity kayıtlarındaki CVSS v3
vektörlerini puanlayan ve ortak finding severity değerlerine dönüştüren katman
eklenmiştir.

Oluşturulan dosyalar:

```text
src/dependency_scanner/osv_severity.py
tests/test_osv_severity.py
```

### Public API

```python
from dependency_scanner import (
    CvssV3VectorError,
    calculate_cvss_v3_base_score,
    classify_cvss_score,
)
```

Base score hesabı:

```python
score = calculate_cvss_v3_base_score(
    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
)

assert score == 9.8
```

Qualitative severity dönüşümü:

```python
severity = classify_cvss_score(score)

assert severity is VulnerabilitySeverity.CRITICAL
```

### Desteklenen Davranış

CVSS `3.0` ve `3.1` base vektörleri FIRST formülüne göre hesaplanır. Bütün
base metric değerleri zorunludur; metric sırası serbesttir ve duplicate,
bilinmeyen veya geçersiz metric değerleri reddedilir.

Geçerli temporal ve environmental metric değerleri kabul edilir ancak bu API
yalnızca base score hesapladığı için puanı değiştirmez.

Qualitative severity aralıkları:

```text
0.0       -> UNKNOWN
0.1-3.9   -> LOW
4.0-6.9   -> MEDIUM
7.0-8.9   -> HIGH
9.0-10.0  -> CRITICAL
```

Ortak severity modelinde `NONE` bulunmadığı için CVSS `0.0` sonucu `UNKNOWN`
olarak temsil edilir.

### OSV Source Entegrasyonu

`OsvVulnerabilitySource`, sorgulanan dependency ile aynı normalize edilmiş
ada ve `PyPI` ecosystem değerine sahip `affected` kaydındaki paket özelinde
severity değerini öncelikli kullanır. Paket özelinde severity bulunmazsa
vulnerability düzeyi severity kayıtları değerlendirilir.

Birden fazla geçerli `CVSS_V3` kaydı varsa en yüksek base score seçilir.
Geçersiz vektörler finding üretimini durdurmaz; desteklenen geçerli bir kayıt
yoksa severity `UNKNOWN` kalır.

Bu aşamada aşağıdaki OSV severity türleri puanlanmaz:

- `CVSS_V2`
- `CVSS_V4`
- `Ubuntu`

### Test Sonuçları

```text
OSV CVSS v3 severity tests: 31 passed
OSV Vulnerability Source tests: 23 passed
Complete test suite: 655 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Uygulanan Dependency Scan Orchestrator

Dependency scanner bileşenine bir requirements dosyasındaki bütün
dependency'leri ortak vulnerability source üzerinden sırasıyla tarayan
orchestration katmanı eklenmiştir.

Oluşturulan dosyalar:

```text
src/dependency_scanner/scanner.py
tests/test_dependency_scanner.py
```

### Public API

```python
from dependency_scanner import (
    DependencyScanError,
    DependencyScanner,
    DependencyScanResult,
    OsvVulnerabilitySource,
    VulnerabilitySourceError,
)
```

Requirements dosyası taraması:

```python
scanner = DependencyScanner(
    OsvVulnerabilitySource()
)

result = scanner.scan_requirements(
    "requirements.txt"
)
```

Önceden ayrıştırılmış dependency değerleri de doğrudan taranabilir:

```python
result = scanner.scan_dependencies(
    dependencies
)
```

### Tarama Sonucu

`DependencyScanResult` aşağıdaki immutable tuple alanlarını içerir:

- `dependencies`
- `findings`
- `errors`

Beklenen source hatası bulunmadığında:

```python
assert result.succeeded
```

değeri `True` olur.

Finding değerleri önce dependency giriş sırasını, ardından source tarafından
döndürülen sıralamayı korur. Duplicate dependency değerleri ayrı lookup
işlemleri olarak korunur.

### Kontrollü Hata Devamlılığı

Beklenen vulnerability source hataları ortak:

```python
VulnerabilitySourceError
```

taban sınıfıyla temsil edilir. Mevcut `OsvQueryError` bu taban sınıftan türer
ve önceki public davranışını korur.

Bir dependency sorgusu `VulnerabilitySourceError` ürettiğinde scanner:

1. Dependency, advisory source ve hata mesajını `DependencyScanError` olarak
   kaydeder.
2. Sıradaki dependency'yi taramaya devam eder.
3. Sonucu `succeeded=False` değeriyle döndürür.

Boş source hata mesajı okunabilir bir varsayılan mesajla değiştirilir.
Beklenmeyen `TypeError`, `AssertionError` ve diğer programlama hataları
gizlenmeden caller'a aktarılır.

Requirements dosyasının okunmasını veya tamamının ayrıştırılmasını engelleyen
dosya ve parser hataları da dönüştürülmeden caller'a aktarılır. Böyle bir
durumda kısmi source taraması başlatılmaz.

### Sorumluluk Sınırları

Orchestrator:

- Requirements satırlarını yeniden ayrıştırmaz; mevcut parser'ı kullanır.
- Paket adını normalize etmez.
- HTTP isteği veya OSV response ayrıştırması yapmaz.
- CVSS score hesaplamaz.
- Retry veya cache uygulamaz.
- Terminal ve JSON raporu oluşturmaz.
- Exit code hesaplamaz.

### Test Sonuçları

```text
Dependency scan orchestrator tests: 34 passed
Complete test suite: 689 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Uygulanan Dependency Scan Formatters

Dependency scan sonuçlarını insan tarafından okunabilir text ve makine
tarafından okunabilir JSON belgelerine dönüştüren formatter katmanı
eklenmiştir.

Oluşturulan dosyalar:

```text
src/dependency_scanner/formatters/__init__.py
src/dependency_scanner/formatters/text.py
src/dependency_scanner/formatters/json.py
tests/test_dependency_text_formatter.py
tests/test_dependency_json_formatter.py
```

### Public API

Her iki formatter paket seviyesinden import edilebilir:

```python
from dependency_scanner import (
    format_dependency_scan_json,
    format_dependency_scan_text,
)
```

Formatter'lar tamamlanmış bir `DependencyScanResult` kabul eder ve string
değer döndürür:

```python
text_report = format_dependency_scan_text(result)
json_report = format_dependency_scan_json(result)
```

Geçersiz result türleri `ValueError` ile reddedilir.

### Text Çıktısı

Text formatter finding değerlerinde severity, advisory kimliği, dependency,
kaynak konumu, mesaj, advisory source ve varsa düzeltilmiş sürüm ile alias
değerlerini gösterir:

```text
[HIGH] OSV-EXAMPLE sample-package==1.0.0 requirements.txt:2 - Example vulnerability. | source=OSV | fixed=2.0.0 | aliases=CVE-2099-0001
```

Lookup hataları ayrı bir kayıt biçimi kullanır:

```text
[LOOKUP ERROR] OSV sample-package==1.0.0 requirements.txt:2 - Service unavailable.
```

Finding kayıtları kendi sıralarıyla önce, lookup error kayıtları kendi
sıralarıyla sonra gösterilir. Finding ve error bulunmayan sonuç okunabilir
bir temiz tarama mesajı içerir.

Her rapor scanned dependency, finding ve lookup error sayılarını doğru tekil
ve çoğul sözcüklerle özetler:

```text
2 dependencies scanned. 1 finding. 1 lookup error.
```

### JSON Çıktısı

JSON formatter aşağıdaki kararlı top-level alanları üretir:

```text
dependencies
findings
errors
summary
```

Dependency ve finding kayıtları mevcut model `to_dict()` sözleşmelerini
kullanır. Error kayıtları dependency, advisory source ve hata mesajını
birlikte serialize eder.

`summary` nesnesi:

- Dependency sayısını
- Finding sayısını
- Error sayısını
- Taramanın bütün lookup işlemleri için başarılı olup olmadığını

içerir.

JSON çıktısı iki space indentation kullanır, Unicode metni korur, collection
sıralarını değiştirmez ve trailing newline eklemez.

### Saf Formatter Davranışı

Her iki formatter:

- Result veya nested model değerlerini değiştirmez.
- Terminale yazmaz.
- Dosya oluşturmaz.
- Dependency taraması başlatmaz.
- HTTP isteği göndermez.
- Exit code hesaplamaz.

### Test Sonuçları

```text
Dependency text formatter tests: 22 passed
Dependency JSON formatter tests: 16 passed
Complete test suite: 727 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Uygulanan Dependency Scan CLI

Dependency scanner orchestration ve formatter katmanlarını çalıştıran bağımsız
bir command-line interface eklenmiştir.

Console command:

```text
securecode-dependency-scan
```

Mevcut `securecode-analyzer` static analysis komutu değişmeden korunmuştur.

Oluşturulan dosyalar:

```text
src/dependency_scanner/cli.py
src/dependency_scanner/default_factory.py
src/dependency_scanner/runner.py
tests/test_dependency_cli.py
tests/test_dependency_runner.py
```

### Temel Kullanım

Bir requirements dosyasını OSV üzerinden taramak için:

```powershell
securecode-dependency-scan requirements.txt
```

JSON çıktısı almak için:

```powershell
securecode-dependency-scan requirements.txt --format json
```

Raporu UTF-8 dosyasına yazmak için:

```powershell
securecode-dependency-scan requirements.txt `
    --format json `
    --output reports/dependencies.json
```

`--output` kullanılmadığında rapor stdout'a yazılır. Output dosyasının parent
klasörü otomatik oluşturulmaz. Requirements input dosyasının output hedefi
olarak kullanılması, input verisinin ezilmesini önlemek için reddedilir.

### Desteklenen Parametreler

```text
requirements_file
--format text|json
--output PATH
--fail-on any|low|medium|high|critical
--source osv
--timeout SECONDS
```

Varsayılan değerler:

```text
format: text
output: stdout
fail-on: any
source: osv
timeout: 10.0
```

Timeout pozitif ve finite bir sayı olmalıdır. İlk CLI sürümünde yalnızca OSV
vulnerability source desteklenmektedir.

### Severity Eşiği

Varsayılan `--fail-on any`, `unknown` dahil bütün finding değerlerinde exit
code `1` üretir.

Belirli bir qualitative severity eşiği seçilebilir:

```powershell
securecode-dependency-scan requirements.txt --fail-on high
```

Eşik sırası:

```text
low < medium < high < critical
```

Örneğin `--fail-on high`, `HIGH` ve `CRITICAL` finding değerlerinde exit code
`1`; `UNKNOWN`, `LOW` ve `MEDIUM` finding değerlerinde exit code `0` üretir.

### Exit Code Politikası

```text
0: Tarama başarılı ve seçilen eşiği karşılayan finding yok
1: Tarama başarılı ve seçilen eşiği karşılayan finding var
2: Kullanıcı, dosya, parse, source veya lookup hatası var
```

Bir veya daha fazla dependency lookup işlemi başarısız olduğunda exit code
`2`, finding exit code değerinden önceliklidir. Başarılı lookup finding
değerleri ve başarısız lookup kayıtları aynı kısmi raporda korunur.

Fatal requirements veya output dosyası hataları stderr'e aşağıdaki biçimde
yazılır:

```text
Error: <message>
```

### Default Component Yapısı

CLI default factory aşağıdaki component zincirini her çağrıda yeniden kurar:

```text
OsvQueryClient
  -> OsvVulnerabilitySource
    -> DependencyScanner
```

`--timeout` değeri doğrudan OSV query client'a aktarılır. Runner mevcut
scanner ve formatter davranışlarını yeniden kullanır; requirements parsing,
HTTP response işleme veya CVSS hesaplama sorumluluklarını tekrar uygulamaz.

### Test Sonuçları

```text
Dependency CLI argument tests: 37 passed
Dependency runner and factory tests: 47 passed
Complete test suite: 811 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Gerçek OSV Fixture ve Offline Entegrasyon

Dependency scanner'ın production katmanları, resmî OSV verisinden hazırlanmış
yerel bir fixture ve örnek requirements dosyasıyla uçtan uca doğrulanmıştır.

Fixture dosyaları:

```text
tests/fixtures/osv/fastapi-0.109.0.json
tests/fixtures/requirements/fastapi-vulnerable.txt
```

Entegrasyon testleri:

```text
tests/test_dependency_integration.py
```

Testler çalışma sırasında internet bağlantısı kullanmaz.

### Resmî Veri Kaynağı

Fixture 18 Ağustos 2026 tarihinde aşağıdaki resmî OSV query ile
doğrulanmıştır:

```text
POST https://api.osv.dev/v1/query
```

Query payload:

```json
{
  "package": {
    "name": "fastapi",
    "ecosystem": "PyPI"
  },
  "version": "0.109.0"
}
```

Kullanılan gerçek advisory:

- [PYSEC-2024-38](https://osv.dev/vulnerability/PYSEC-2024-38)
- [OSV API query endpoint](https://api.osv.dev/v1/query)

Fixture; parser ve source tarafından tüketilen advisory ID, details, aliases,
affected package, GIT/ECOSYSTEM range event ve CVSS v3 alanlarını resmî
değerleri değiştirmeden korur. Tüketilmeyen timestamp, reference ve affected
version listeleri fixture boyutunu deterministik ve incelenebilir tutmak için
eklenmemiştir.

Fixture içindeki `_fixture` metadata nesnesi query bilgisi, capture tarihi,
advisory bağlantısı ve projection politikasını saklar.

### Gerçek Requirements Örneği

```text
fastapi==0.109.0
```

Offline entegrasyon akışı:

```text
requirements fixture
  -> requirements parser
  -> DependencyScanner
  -> OsvVulnerabilitySource
  -> fixture query client
  -> OSV response parser
  -> DependencyFinding
  -> text/JSON formatter
  -> dependency CLI runner
```

Bu akış aşağıdaki gerçek finding değerini üretir:

```text
advisory: PYSEC-2024-38
alias: CVE-2024-24762
package: fastapi==0.109.0
fixed version: 0.109.1
severity: HIGH
source: OSV
```

### Fixed Version Düzeltmesi

Gerçek OSV kaydı aynı affected package içinde önce bir `GIT`, ardından bir
`ECOSYSTEM` range içerir. Önceki source davranışı ilk fixed event değerini
koşulsuz seçtiği için aşağıdaki commit SHA değerini paket sürümü olarak
raporlayabilirdi:

```text
9d34ad0ee8a0dfbbcce06f76c2d5d851085024fc
```

Fixed-version seçimi artık yalnızca:

- Taranan dependency adıyla normalize edilmiş biçimde eşleşen
- `PyPI` ecosystem değerine sahip
- `ECOSYSTEM` range türündeki

fixed event kayıtlarını değerlendirir.

Doğru sonuç:

```text
0.109.1
```

Başka package, başka ecosystem ve `GIT` range fixed değerleri yok sayılır.
Eşleşen package version fix bulunmadığında `fixed_version=None` korunur.

### Entegrasyon Doğrulamaları

Offline testler:

- Fixture provenance ve query metadata değerlerini doğrular.
- Requirements fixture değerini production parser ile okur.
- OSV fixture değerini production response parser ile ayrıştırır.
- Query package, version ve page token değerlerini doğrular.
- Advisory ID ve CVE alias değerlerini korur.
- ECOSYSTEM fixed version değerini seçer.
- Commit SHA değerinin rapora sızmadığını doğrular.
- CVSS v3 vector değerini `HIGH` severity olarak sınıflandırır.
- Text ve JSON raporlarını doğrular.
- CLI `any`, `high` ve `critical` eşiklerini doğrular.
- UTF-8 JSON output dosyasını doğrular.
- Canlı HTTP çağrısını engeller.

### Test Sonuçları

```text
OSV Vulnerability Source tests: 27 passed
Offline dependency integration tests: 13 passed
Complete test suite: 828 passed
Compile check: passed
Self-analysis: No findings found.
Exit code: 0
```

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
