# Static Code Analyzer

## Amaç

Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve
güvenlik problemlerini tespit etmek.

## Kullanılan Yöntemler

- Python kodunun yapısal analizi için `ast`
- Metin tabanlı kontroller için satır taraması ve regex
- Otomatik testler için `pytest`

## Mevcut Analiz Kuralları

### SA001 — Long Function

Yapılandırılmış satır sınırını aşan normal ve asenkron fonksiyonları tespit
eder.

Varsayılan eşik:

```text
50 satır
```

Varsayılan önem seviyesi:

```text
WARNING
```

Örnek kullanım:

```python
import ast

from static_analyzer.rules import LongFunctionRule

source = """
def example_function():
    value_1 = 1
    value_2 = 2
"""

tree = ast.parse(source)
rule = LongFunctionRule(max_lines=2)

findings = rule.check(tree, "example.py")
```

Kural aşağıdaki durumları destekler:

- Normal fonksiyonlar
- Asenkron fonksiyonlar
- İç içe fonksiyonlar
- Yapılandırılabilir satır sınırı
- Aynı dosyada birden fazla bulgu

### SA002 — Long Class

Yapılandırılmış satır sınırını aşan Python sınıflarını tespit eder.

Varsayılan eşik:

```text
200 satır
```

Varsayılan önem seviyesi:

```text
WARNING
```

Örnek kullanım:

```python
import ast

from static_analyzer.rules import LongClassRule

source = """
class DataProcessor:
    first_value = 1
    second_value = 2
"""

tree = ast.parse(source)
rule = LongClassRule(max_lines=2)

findings = rule.check(tree, "example.py")
```

Kural aşağıdaki durumları destekler:

- Python sınıf tanımları
- İç içe sınıflar
- Yapılandırılabilir satır sınırı
- Aynı dosyada birden fazla bulgu
- Geçersiz eşik değerlerinin reddedilmesi
## Python Dosya Tarayıcı

`FileScanner`, kullanıcı tarafından verilen hedef dizindeki Python kaynak
dosyalarını bulur.

Modül:

```text
src/static_analyzer/file_scanner.py
```

Örnek kullanım:

```python
from static_analyzer.file_scanner import FileScanner

scanner = FileScanner()
python_files = scanner.scan("src")

for python_file in python_files:
    print(python_file)
```

Tarayıcı aşağıdaki davranışları destekler:

- `str` ve `pathlib.Path` hedefleri
- Alt klasörlerin özyinelemeli taranması
- Yalnızca `.py` dosyalarının bulunması
- Sonuçların sıralı döndürülmesi
- Sonuçların `Path` nesneleri olarak döndürülmesi
- Mevcut olmayan hedeflerin reddedilmesi
- Dosya olarak verilen hedeflerin reddedilmesi
- Özel klasör hariç tutma desteği
- Sembolik bağlantılı dizinlerin takip edilmemesi

Varsayılan olarak tarama dışında bırakılan dizinler:

```text
.git
.venv
__pycache__
```

Özel hariç tutulan dizinler oluşturucu üzerinden eklenebilir:

```python
scanner = FileScanner(
    excluded_directories={
        "generated",
        "vendor",
    }
)
```

Özel dizinler varsayılan hariç tutmalara eklenir; varsayılan dizinler
kaldırılmaz.
## Python Kaynak Kod Okuyucu

`SourceReader`, Python kaynak dosyalarını UTF-8 olarak okur ve kaynak kodu
AST yapısına dönüştürür.

### AnalysisEngine

`AnalysisEngine`, parse edilmiş bir `SourceFile` üzerinde kayıtlı analiz
kurallarını çalıştırır.

### BaseTextRule

`BaseTextRule`, AST içerisinde doğrudan korunmayan kaynak kod bilgilerinin
incelenmesi için kullanılan soyut kural arayüzüdür.

Metin tabanlı kurallar aşağıdaki bilgileri alır:

- Kaynak dosyanın tam metni
- Kaynak dosyanın yolu

Somut bir metin tabanlı kural aşağıdaki sözleşmeyi uygular:

```python
def check(
    self,
    source: str,
    file_path: str,
) -> list[Finding]:
    ...
```### TodoFixmeRule

`TodoFixmeRule`, Python yorum satırlarında bulunan `TODO` ve `FIXME`
ifadelerini tespit eden metin tabanlı analiz kuralıdır.

Kural kimliği:

```text
SA003
```

Kural, Python standart kütüphanesindeki `tokenize` modülünü kullanır.
Yalnızca `COMMENT` token türleri incelendiği için string literal içerisindeki
`TODO` ve `FIXME` ifadeleri bulgu oluşturmaz.

Örnek:

```python
source = """
# TODO: add input validation
value = 1
# FIXME: remove temporary fallback
"""

rule = TodoFixmeRule()
findings = rule.check(source, "example.py")
```

Kuralın önem seviyeleri:

- `TODO`: `INFO`
- `FIXME`: `WARNING`

Her bağımsız ifade için ayrı bir `Finding` oluşturulur. Bulgular gerçek dosya
yolunu, satır numarasını ve bir tabanlı sütun numarasını içerir.
### EmptyExceptRule

`EmptyExceptRule`, yalnızca `pass` ifadelerinden oluşan Python exception
handler bloklarını tespit eden AST tabanlı analiz kuralıdır.

Kural kimliği:

```text
SA004
```

Kural, mevcut AST yapısındaki `ast.ExceptHandler` düğümlerini inceler:

```python
try:
    risky_operation()
except Exception:
    pass
```

Bare except blokları da desteklenir:

```python
try:
    risky_operation()
except:
    pass
```

Bir handler içerisinde `pass` dışında gerçek bir işlem bulunuyorsa bulgu
oluşturulmaz:

```python
try:
    risky_operation()
except Exception as error:
    logger.exception(error)
```

Her bulgu aşağıdaki bilgileri içerir:

- `SA004` kural kimliği
- `Empty except block found.` mesajı
- Gerçek dosya yolu
- `except` satır ve sütun konumu
- `WARNING` önem seviyesi

İç içe ve birden fazla boş exception handler ayrı bulgular olarak raporlanır.
### HardcodedSecretRule

`HardcodedSecretRule`, hassas isimli değişkenlere doğrudan atanmış string
literal değerlerini tespit eden AST tabanlı analiz kuralıdır.

Kural kimliği:

```text
SA005
```

Bulgu üreten örnekler:

```python
password = "admin123"
database_password = "secret-value"
api_key = "abc123"
client_secret: str = "client-secret-value"
config.password = "admin123"
```

Kural aşağıdaki hassas isimleri ve bunları içeren `snake_case` hedefleri
büyük-küçük harf duyarsız olarak kontrol eder:

- `password`
- `passwd`
- `pwd`
- `secret`
- `token`
- `api_key`
- `apikey`
- `access_token`
- `auth_token`
- `client_secret`
- `private_key`

Yalnızca boş olmayan string literal değerleri raporlanır. Çalışma anında
alınan veya fonksiyonlar tarafından döndürülen değerler bulgu üretmez:

```python
api_key = os.getenv("API_KEY")
secret = load_secret()
password = None
token = ""
```

Her bulgu aşağıdaki bilgileri içerir:

- `SA005` kural kimliği
- `Possible hardcoded secret found.` mesajı
- Gerçek dosya yolu
- Hassas atama hedefinin satır ve sütun konumu
- `WARNING` önem seviyesi

Gerçek secret değeri bulgu mesajına eklenmez. Bu kural kesinleşmiş bir
güvenlik açığı yerine incelenmesi gereken şüpheli bir durumu bildirir.
### NamingConventionRule

`NamingConventionRule`, Python kaynak kodundaki fonksiyon, metot ve sınıf
isimlerini AST üzerinden kontrol eden isimlendirme kuralıdır.

Kural kimliği:

```text
SA006
```

Fonksiyon ve metot isimleri `snake_case` biçiminde olmalıdır:

```python
def calculate_total() -> int:
    return 0


async def fetch_user_data() -> None:
    pass


def _internal_helper() -> None:
    pass
```

Aşağıdaki isimler bulgu üretir:

```python
def CalculateTotal() -> int:
    return 0


def calculateTotal() -> int:
    return 0


async def FetchUserData() -> None:
    pass
```

Geçersiz fonksiyon ve metot isimleri için üretilen mesaj:

```text
Function name should use snake_case.
```

`__init__` ve `__str__` gibi çift alt çizgiyle başlayıp biten Python özel
metotları kontrol dışında tutulur:

```python
class Example:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Example"
```

Sınıf isimleri `PascalCase` biçiminde olmalıdır:

```python
class UserService:
    pass


class HTTPClient:
    pass


class _InternalHandler:
    pass
```

Aşağıdaki sınıf isimleri bulgu üretir:

```python
class user_service:
    pass


class userService:
    pass
```

Geçersiz sınıf isimleri için üretilen mesaj:

```text
Class name should use PascalCase.
```

Kural aşağıdaki yapıların tamamını kontrol eder:

- Modül seviyesindeki fonksiyonlar
- Normal ve asenkron fonksiyonlar
- Sınıf metotları
- İç içe fonksiyonlar
- İç içe sınıflar

Her bulgu aşağıdaki bilgileri içerir:

- `SA006` kural kimliği
- Gerçek kaynak dosya yolu
- Tanımın satır numarası
- Bir tabanlı sütun numarası
- Fonksiyon veya sınıfa uygun mesaj
- `INFO` önem seviyesi

Kural kaynak dosyayı tekrar okumaz, kodu yeniden parse etmez ve kendisine
verilen AST nesnesini değiştirmez.
### ProjectAnalyzer

`ProjectAnalyzer`, hedef klasördeki bütün Python kaynak dosyalarının analiz
edilmesini yöneten üst seviye koordinasyon bileşenidir.

Aşağıdaki mevcut bileşenleri bir araya getirir:

- `FileScanner`
- `SourceReader`
- `AnalysisEngine`

Temel kullanım:

```python
from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.file_scanner import FileScanner
from static_analyzer.project_analyzer import ProjectAnalyzer
from static_analyzer.source_reader import SourceReader

scanner = FileScanner()
reader = SourceReader()
engine = AnalysisEngine(rules=[])

analyzer = ProjectAnalyzer(
    scanner=scanner,
    reader=reader,
    engine=engine,
)

findings = analyzer.analyze("src")
```

Analiz işlemi aşağıdaki sırayla gerçekleşir:

1. `FileScanner.scan()` hedef klasördeki Python dosyalarını keşfeder.
2. Her dosya `SourceReader.read()` ile okunur ve AST nesnesine dönüştürülür.
3. Her `SourceFile`, `AnalysisEngine.analyze()` metoduna verilir.
4. Dosyalardan dönen bulgular tek listede birleştirilir.
5. Bulgular kararlı bir sırada döndürülür.

Bulgular aşağıdaki ölçütlere göre sıralanır:

1. Dosya yolu
2. Satır numarası
3. Sütun numarası
4. Kural kimliği

Sütun numarası bulunmayan bulgular sıralama sırasında `0` olarak
değerlendirilir.

```python
(
    finding.file_path.casefold(),
    finding.line_number,
    finding.column_number or 0,
    finding.rule_id,
)
```

Hedef klasörde Python dosyası bulunmuyorsa boş liste döndürülür:

```python
[]
```

Bu durumda kaynak okuyucu ve analiz motoru çağrılmaz.

`ProjectAnalyzer`, alt bileşenlerden gelen hataları gizlemez. Örneğin:

- `FileNotFoundError`
- `NotADirectoryError`
- `SyntaxError`
- `UnicodeDecodeError`
- Analiz motorundan gelen beklenmeyen hatalar

olduğu gibi çağıran katmana iletilir.

Bileşen aşağıdaki işlemleri gerçekleştirmez:

- Terminal çıktısı üretmek
- JSON çıktısı oluşturmak
- Process exit code belirlemek
- Kaynak dosyaları değiştirmek
- AST nesnelerini değiştirmek
- Kendi içinde analiz kuralları oluşturmak
- Dependency veya CVE analizi yapmak

`AnalysisEngine`, kural türüne göre doğru girdiyi gönderir:

- `BaseRule` kurallarına `SourceFile.tree`
- `BaseTextRule` kurallarına `SourceFile.source`

Örnek metin tabanlı kural:

```python
from static_analyzer.models import Finding
from static_analyzer.rules import BaseTextRule


class ExampleTextRule(BaseTextRule):
    rule_id = "TEXT001"
    name = "Example Text Rule"
    description = "Example source text analysis rule."

    def check(
        self,
        source: str,
        file_path: str,
    ) -> list[Finding]:
        return []
```

AST ve metin tabanlı kurallar aynı analiz motorunda birlikte
kullanılabilir:

```python
engine = AnalysisEngine(
    rules=[
        LongFunctionRule(),
        ExampleTextRule(),
        LongClassRule(),
    ]
)
```

Kurallar motor içerisine verildikleri sırayla çalıştırılır ve ürettikleri
bulgular aynı sırayla ortak listede birleştirilir.

Motorun temel sorumlulukları:

- Analiz kurallarını değiştirilemez bir `tuple` içerisinde saklamak
- Her kuralı aynı AST nesnesi üzerinde çalıştırmak
- Gerçek kaynak dosya yolunu kurallara iletmek
- Kuralların ürettiği bulguları ortak bir listede toplamak
- Kural ve bulgu sırasını korumak
- Kaynak kodun tekrar parse edilmesini önlemek
- Beklenmeyen kural exception'larını gizlememek

Örnek kullanım:

```python
from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.rules import LongClassRule, LongFunctionRule
from static_analyzer.source_reader import SourceReader

source_file = SourceReader().read("example.py")

engine = AnalysisEngine(
    rules=[
        LongFunctionRule(),
        LongClassRule(),
    ]
)

findings = engine.analyze(source_file)
```

Modül:

```text
src/static_analyzer/source_reader.py
```

Örnek kullanım:

```python
from static_analyzer.source_reader import SourceReader

reader = SourceReader()
source_file = reader.read("example.py")

print(source_file.file_path)
print(source_file.source)
print(source_file.tree)
```

Okuma işlemi sonucunda bir `SourceFile` nesnesi döndürülür:

```python
@dataclass(frozen=True, slots=True)
class SourceFile:
    file_path: Path
    source: str
    tree: ast.AST
```

Kaynak kod okuyucu aşağıdaki davranışları destekler:

- `str` ve `pathlib.Path` dosya yolları
- UTF-8 kaynak kod okuma
- Kaynak kod metninin korunması
- Kaynak kodun `ast.parse()` ile parse edilmesi
- Dosyanın yalnızca bir kez parse edilmesi
- Syntax hatalarında gerçek dosya yolunun gösterilmesi
- Mevcut olmayan dosyaların reddedilmesi
- Dizin olarak verilen hedeflerin reddedilmesi
- UTF-8 olmayan dosyaların reddedilmesi

## Planlanan Kontroller

- Fonksiyon ve sınıf isimlendirme kontrolü
- Hardcoded parola, token veya anahtar tespiti

## Planlanan Girdiler

Araç tamamlandığında aşağıdaki girdileri kabul edecektir:

- Tek bir Python dosyasının yolu
- Python proje klasörünün yolu

Dosya ve klasör tarama mekanizması henüz geliştirilmemiştir.

Mevcut `LongFunctionRule`, doğrudan parse edilmiş bir `ast.AST` nesnesi ve
analiz edilen dosyanın yolunu kabul etmektedir.

## Çıktı

Her bulgu aşağıdaki bilgileri içerir:

- Kural kimliği
- Dosya yolu
- Satır numarası
- Varsa sütun numarası
- Önem seviyesi
- Problem açıklaması

## Test

Bütün testler aşağıdaki komutla çalıştırılır:

```bash
python -m pytest -v
```

Mevcut durumda toplam 47 test bulunmaktadır.

- 10 test `LongFunctionRule` davranışlarını doğrulamaktadır.
- 10 test `LongClassRule` davranışlarını doğrulamaktadır.
- 12 test `FileScanner` davranışlarını doğrulamaktadır.
- 11 test `SourceReader` davranışlarını doğrulamaktadır.
- 4 test ortak veri modeli ve temel kural arayüzünü doğrulamaktadır.

Bütün testler başarılı şekilde çalışmaktadır.

- 10 test `LongFunctionRule` davranışlarını doğrulamaktadır.
- 10 test `LongClassRule` davranışlarını doğrulamaktadır.
- 4 test ortak veri modeli ve temel kural arayüzünü doğrulamaktadır.

## Dokümantasyon

- [Analiz ve Gereksinimler](analysis.md)
- [Teknik Tasarım](technical-design.md)

## Mevcut Durum

Tamamlanan çalışmalar:

- Ortak `Finding` veri modeli
- `Severity` önem seviyeleri
- Soyut `BaseRule` arayüzü
- `SA001` uzun fonksiyon kuralı
- Yapılandırılabilir fonksiyon uzunluğu sınırı
- Normal ve asenkron fonksiyon desteği
- İç içe fonksiyon desteği
- Unit testler
- `SA002` uzun sınıf kuralı
- Yapılandırılabilir sınıf uzunluğu sınırı
- İç içe sınıf desteği
- Geçersiz sınıf eşiği doğrulaması
- Python dosya tarayıcı geliştirildi.
- Alt klasörlerdeki `.py` dosyalarının bulunması sağlandı.
- Varsayılan ve özel klasör hariç tutma desteği eklendi.
- Sembolik bağlantılı dizinlerin takip edilmesi engellendi.
- Dosya yollarının sıralı `Path` nesneleri olarak döndürülmesi sağlandı.
- Dosya tarayıcı 12 test senaryosuyla doğrulandı.
- `SourceFile` veri modeli geliştirildi.
- `SourceReader` sınıfı geliştirildi.
- Python kaynak dosyalarının UTF-8 olarak okunması sağlandı.
- Kaynak kodun AST yapısına dönüştürülmesi sağlandı.
- Syntax ve encoding hatalarının gizlenmeden iletilmesi sağlandı.
- Kaynak kod okuyucu 11 test senaryosuyla doğrulandı.
- `AnalysisEngine` sınıfı geliştirildi.
- Birden fazla analiz kuralının aynı AST üzerinde çalıştırılması sağlandı.
- Kural bulgularının ortak bir listede birleştirilmesi sağlandı.
- Analiz motoru 12 test senaryosuyla doğrulandı.
- `BaseTextRule` soyut arayüzü geliştirildi.
- Metin tabanlı kurallar için kaynak metin analizi desteği eklendi.
- `AnalysisEngine` içerisinde AST ve metin tabanlı kural desteği birleştirildi.
- Karma kural çalıştırma sırasının korunması sağlandı.
- Metin tabanlı kural altyapısı 12 test senaryosuyla doğrulandı.
- `TodoFixmeRule` metin tabanlı analiz kuralı geliştirildi.
- Python yorumlarının `tokenize` ile güvenli biçimde incelenmesi sağlandı.
- `TODO` bulguları `INFO`, `FIXME` bulguları `WARNING` olarak raporlandı.
- String literal ve identifier içerisindeki ifadelerin yok sayılması sağlandı.
- `TodoFixmeRule` 19 test senaryosuyla doğrulandı.
- `EmptyExceptRule` AST tabanlı analiz kuralı geliştirildi.
- Yalnızca `pass` içeren exception handler bloklarının tespiti sağlandı.
- Typed, bare ve `except*` handler desteği eklendi.
- Gerçek işlem veya `raise` içeren handler bloklarının yok sayılması sağlandı.
- İç içe ve birden fazla boş handler desteği eklendi.
- `EmptyExceptRule` 19 test senaryosuyla doğrulandı.
- `HardcodedSecretRule` AST tabanlı analiz kuralı geliştirildi.
- Hassas değişken ve attribute isimlerinin tespit edilmesi sağlandı.
- Normal, annotated ve birden fazla hedef içeren atamalar desteklendi.
- Yalnızca boş olmayan string literal değerlerinin raporlanması sağlandı.
- Ortam değişkeni ve fonksiyon çağrılarının yok sayılması sağlandı.
- Secret değerlerinin bulgu mesajında gösterilmemesi sağlandı.
- `HardcodedSecretRule` 22 test senaryosuyla doğrulandı.
- `NamingConventionRule` AST tabanlı analiz kuralı geliştirildi.
- Fonksiyon ve metot isimlerinin `snake_case` biçiminde kontrol edilmesi sağlandı.
- Sınıf isimlerinin `PascalCase` biçiminde kontrol edilmesi sağlandı.
- Normal ve asenkron fonksiyonların desteklenmesi sağlandı.
- Sınıf metotlarının ve iç içe tanımların kontrol edilmesi sağlandı.
- Python özel metotlarının isimlendirme kontrolü dışında tutulması sağlandı.
- İsimlendirme bulgularının `INFO` önem seviyesinde üretilmesi sağlandı.
- `NamingConventionRule` 25 test senaryosuyla doğrulandı.
- `ProjectAnalyzer` proje seviyesinde analiz koordinasyon bileşeni geliştirildi.
- `FileScanner`, `SourceReader` ve `AnalysisEngine` bileşenleri birleştirildi.
- Hedef klasördeki bütün Python dosyalarının işlenmesi sağlandı.
- Her dosyanın yalnızca bir kez okunması ve analiz edilmesi sağlandı.
- Farklı dosyalardan gelen bulguların tek listede birleştirilmesi sağlandı.
- Bulguların dosya, satır, sütun ve kural kimliğine göre sıralanması sağlandı.
- `None` sütun numaralarının güvenli biçimde sıralanması sağlandı.
- Alt bileşenlerden gelen hataların değiştirilmeden iletilmesi sağlandı.
- `ProjectAnalyzer` 20 test senaryosuyla doğrulandı.
- Projedeki toplam 176 test başarıyla çalıştırıldı.


Henüz tamamlanmayan çalışmalar:

- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- CI/CD entegrasyonu

## 17. Navigation

- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)