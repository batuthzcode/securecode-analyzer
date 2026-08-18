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
### Default Analyzer Factory

Default analyzer factory, statik analiz sisteminin varsayılan bileşenlerini
tek bir noktada oluşturur.

Factory modülü iki public fonksiyon sağlar:

```python
from static_analyzer.default_factory import (
    create_default_analyzer,
    create_default_rules,
)
```
### CLI Foundation

CLI foundation, SecureCode Analyzer komut satırı arayüzünün argüman
ayrıştırma katmanını sağlar.

Modül:

```text
src/static_analyzer/cli.py
```

Public bileşenler:

```python
from static_analyzer.cli import (
    CliArguments,
    build_parser,
    parse_arguments,
)
```
### Text Formatter

Text formatter, statik analiz bulgularını kullanıcı tarafından okunabilir
terminal metnine dönüştürür.

Modül yapısı:

```text
src/static_analyzer/formatters/__init__.py
src/static_analyzer/formatters/text.py
```

Public fonksiyon:

```python
from static_analyzer.formatters import format_findings_text
```

Temel kullanım:

```python
text = format_findings_text(findings)
```

Her bulgu aşağıdaki biçimde gösterilir:

```text
[SEVERITY] RULE_ID FILE_PATH:LINE:COLUMN - MESSAGE
```

Örnek:

```text
[WARNING] SA005 src/example.py:1:1 - Possible hardcoded secret found.
```

Sütun numarası bulunmayan bulgularda yalnızca dosya yolu ve satır numarası
gösterilir:

```text
[INFO] SA003 src/example.py:8 - TODO comment found.
```

`None` değeri terminal metnine yazılmaz.

Birden fazla bulgu ayrı satırlarda gösterilir:

```text
[WARNING] SA005 src/config.py:1:1 - Possible hardcoded secret found.
[INFO] SA006 src/config.py:3:1 - Function name should use snake_case.

2 findings found.
```

Bulgu satırları ile özet arasında bir boş satır bulunur.

Tek bulgu için tekil özet kullanılır:

```text
1 finding found.
```

Birden fazla bulgu için çoğul özet kullanılır:

```text
3 findings found.
```

Bulgu bulunmadığında yalnızca şu metin döndürülür:

```text
No findings found.
```

Formatter aşağıdaki iterable türlerini destekler:

- Liste
- Tuple
- Generator
- Diğer iterable bulgu koleksiyonları

Generator girdileri güvenli biçimde yalnızca bir kez tüketilir.

Formatter kendisine verilen bulguların sırasını korur. Bulguları filtrelemez
veya yeniden sıralamaz. Dosya ve kaynak sıralaması `ProjectAnalyzer`
sorumluluğunda kalır.

Severity değerleri büyük harfle gösterilir:

```text
INFO
WARNING
ERROR
```

Döndürülen string sonunda fazladan yeni satır bulunmaz.

Text formatter:

- Terminale doğrudan yazmaz
- `print()` çağırmaz
- Analiz çalıştırmaz
- CLI argümanlarını parse etmez
- JSON çıktısı üretmez
- Exit code politikası belirlemez
- Bulgu nesnelerini değiştirmez
### JSON Formatter

JSON formatter, statik analiz bulgularını makineler ve diğer uygulamalar
tarafından işlenebilecek JSON metnine dönüştürür.

Modül:

```text
src/static_analyzer/formatters/json.py
```

Public fonksiyon:

```python
from static_analyzer.formatters import format_findings_json
```

Temel kullanım:

```python
json_text = format_findings_json(findings)
```

Üretilen JSON belgesinin üst seviye yapısı:

```json
{
  "findings": [],
  "summary": {
    "total": 0
  }
}
```

Her bulgu aşağıdaki public alanları içerir:

```json
{
  "rule_id": "SA005",
  "message": "Possible hardcoded secret found.",
  "file_path": "src/example.py",
  "line_number": 1,
  "severity": "warning",
  "column_number": 1
}
```

Bulgu verileri mevcut `Finding.to_dict()` metodu üzerinden oluşturulur.

Severity değerleri küçük harfli string olarak gösterilir:

```text
info
warning
error
```

Sütun numarası bulunmayan bulgularda alan kaldırılmaz ve JSON `null`
değeri kullanılır:

```json
{
  "column_number": null
}
```

Birden fazla bulgu `findings` listesinde ayrı nesneler olarak bulunur.
`summary.total` gerçek bulgu sayısını içerir.

```json
{
  "findings": [
    {
      "rule_id": "SA005",
      "message": "Possible hardcoded secret found.",
      "file_path": "src/config.py",
      "line_number": 1,
      "severity": "warning",
      "column_number": 1
    },
    {
      "rule_id": "SA006",
      "message": "Function name should use snake_case.",
      "file_path": "src/config.py",
      "line_number": 3,
      "severity": "info",
      "column_number": 1
    }
  ],
  "summary": {
    "total": 2
  }
}
```

JSON iki boşluk girinti kullanılarak okunabilir biçimde oluşturulur.

Türkçe ve diğer Unicode karakterler doğrudan korunur:

```json
{
  "message": "Güvenlik yapılandırması kontrol edilmeli."
}
```

Formatter aşağıdaki iterable türlerini destekler:

- Liste
- Tuple
- Generator
- Diğer iterable bulgu koleksiyonları

Generator girdileri yalnızca bir kez tüketilir.

JSON formatter:

- Bulguların giriş sırasını korur
- Bulguları sıralamaz veya filtrelemez
- Bulgu nesnelerini değiştirmez
- Dosya yollarını normalize etmez
- Terminale doğrudan yazmaz
- Dosyaya rapor kaydetmez
- Analiz çalıştırmaz
- Exit code politikası belirlemez

Döndürülen JSON string sonunda fazladan yeni satır bulunmaz.
### CLI Runner

CLI runner, SecureCode Analyzer uygulamasının komut satırı çalışma akışını
koordine eder.

Modül:

```text
src/static_analyzer/runner.py
```

Public fonksiyonlar:

```python
from static_analyzer.runner import main, run_cli
```

`run_cli()` aşağıdaki işlem sırasını uygular:

1. CLI argümanlarını ayrıştırır.
2. Varsayılan analyzer nesnesini oluşturur.
3. Hedef klasörü analiz eder.
4. Bulguları seçilen çıktı formatına dönüştürür.
5. Raporu standart çıktıya yazar.
6. `--fail-on` severity eşiğine uygun exit code döndürür.

Temel kullanım:

```python
exit_code = run_cli(["src"])
```

JSON formatı:

```python
exit_code = run_cli(
    [
        "src",
        "--format",
        "json",
    ]
)
```

Severity eşiği:

```python
exit_code = run_cli(
    [
        "src",
        "--fail-on",
        "warning",
    ]
)
```

Runner mevcut bileşenleri kullanır:

```python
parse_arguments()
create_default_analyzer()
format_findings_text()
format_findings_json()
```

Runner kendi parser, analyzer veya formatter uygulamasını oluşturmaz.
### Self-Analysis

SecureCode Analyzer kendi kaynak kodu üzerinde public console script
aracılığıyla doğrulanmıştır.

Analiz hedefi:

```text
src
```

İlk analiz sonucu:

```text
2 findings found.
```

İki bulgu da `SA001` Long Function kuralı tarafından üretilmiştir:

- `HardcodedSecretRule.check()` — 58 satır
- `NamingConventionRule.check()` — 56 satır

Bulgular geçerli kod kalitesi problemleri olarak sınıflandırılmıştır.

Fonksiyonlar davranışları korunarak küçük yardımcı metotlara ayrılmıştır.
Kural eşikleri, kimlikleri, severity değerleri ve bulgu mesajları
değiştirilmemiştir.

Son analiz sonucu:

```text
No findings found.
```

Son exit code:

```text
0
```

Tam test sonucu:

```text
288 passed
```

Ayrıntılı rapor:

```text
docs/components/static-analyzer/self-analysis.md
```

#### Text Çıktısı

Varsayılan çıktı formatı `text` değeridir:

```powershell
securecode-analyzer src
```

Açıkça da seçilebilir:

```powershell
securecode-analyzer src --format text
```

Örnek bulgusuz çıktı:

```text
No findings found.
```

Örnek bulgulu çıktı:

```text
[WARNING] SA005 src/example.py:1:1 - Possible hardcoded secret found.

1 finding found.
```

#### JSON Çıktısı

JSON çıktısı aşağıdaki komutla seçilir:

```powershell
securecode-analyzer src --format json
```

Örnek bulgusuz çıktı:

```json
{
  "findings": [],
  "summary": {
    "total": 0
  }
}
```

Runner formatter tarafından döndürülen çıktının sonuna tam olarak bir yeni
satır ekler.

Başarılı analiz çıktısı standart çıktıya yazılır.

#### Exit Code Politikası

Bulgusuz analiz:

```text
0
```

Seçilen `--fail-on` eşiğini karşılayan bir veya daha fazla bulgu:

```text
1
```

Beklenen operasyonel hata:

```text
2
```

Varsayılan `--fail-on any` bütün severity seviyelerinde bulgu exit code
değerini üretir:

```text
INFO
WARNING
ERROR
```

Bir bulgu yalnızca `INFO` seviyesinde olsa bile exit code `1` olur.

Desteklenen eşikler:

```text
any
info
warning
error
```

`--fail-on warning`, `INFO` bulgularını raporda korur ancak yalnızca `WARNING`
ve `ERROR` bulgularında exit code `1` üretir. `--fail-on error` yalnızca
`ERROR` bulgularında başarısız olur.

#### Operasyonel Hatalar

`main()` aşağıdaki beklenen hataları yönetir:

- `FileNotFoundError`
- `NotADirectoryError`
- `SyntaxError`
- `UnicodeDecodeError`

Bu hatalar standart hata çıktısına aşağıdaki formatta yazılır:

```text
Error: <exception message>
```

Operasyonel hata durumunda:

- Standart çıktıya analiz raporu yazılmaz.
- Standart hata çıktısına hata mesajı yazılır.
- Exit code `2` döndürülür.

Beklenmeyen exception türleri gizlenmez ve çağıran katmana iletilir.

Standart `argparse` davranışı korunur. Eksik argümanlar ve geçersiz
seçenekler `SystemExit(2)`, yardım seçeneği ise `SystemExit(0)` üretir.

#### Console Script

Proje aşağıdaki console script girişini içerir:

```toml
[project.scripts]
securecode-analyzer = "static_analyzer.runner:main"
```

Editable kurulumdan sonra yardım komutu:

```powershell
.\.venv\Scripts\securecode-analyzer.exe --help
```

Analiz komutları:

```powershell
.\.venv\Scripts\securecode-analyzer.exe src

.\.venv\Scripts\securecode-analyzer.exe `
    src `
    --format json
```

CLI runner:

- Bulguları değiştirmez
- Bulguları sıralamaz veya filtrelemez
- Dosya yollarını normalize etmez
- Text formatını tekrar uygulamaz
- JSON formatını tekrar uygulamaz
- Kaynak dosyaları doğrudan okumaz
- Dosya sistemini doğrudan taramaz
- AST oluşturmaz
- Dependency veya CVE taraması yapmaz

#### CliArguments

`CliArguments`, doğrulanmış komut satırı seçeneklerini temsil eden immutable
bir veri sınıfıdır:

```python
@dataclass(frozen=True, slots=True)
class CliArguments:
    target: Path
    output_format: str
    fail_on: str = "any"
```

Alanlar:

- `target`: Analiz edilecek hedef klasörün `Path` karşılığı
- `output_format`: `text` veya `json`
- `fail_on`: `any`, `info`, `warning` veya `error`

#### Hedef yol

CLI bir zorunlu positional hedef yol kabul eder:

```powershell
securecode-analyzer src
securecode-analyzer .
securecode-analyzer C:\projects\example
```

Parser hedef yolun varlığını veya klasör olup olmadığını kontrol etmez.
Bu kontroller analiz sırasında `FileScanner` tarafından gerçekleştirilir.

#### Output formatı

Varsayılan çıktı formatı:

```text
text
```

JSON formatı açıkça seçilebilir:

```powershell
securecode-analyzer src --format json
```

Desteklenen değerler:

```text
text
json
```

Geçersiz bir format standart `argparse` kullanım hatası üretir:

```powershell
securecode-analyzer src --format xml
```

#### Fail-on eşiği

Varsayılan eşik:

```text
any
```

Severity gate örneği:

```powershell
securecode-analyzer src --fail-on warning
```

Eşik sırası:

```text
info < warning < error
```

#### Parser oluşturma

Her `build_parser()` çağrısı yeni bir `ArgumentParser` nesnesi üretir:

```python
first_parser = build_parser()
second_parser = build_parser()

assert first_parser is not second_parser
```

Program adı:

```text
securecode-analyzer
```

Program açıklaması:

```text
Analyze Python source code for quality and security findings.
```

#### Argüman ayrıştırma

Argümanlar doğrudan bir liste üzerinden ayrıştırılabilir:

```python
arguments = parse_arguments(
    [
        "src",
        "--format",
        "json",
        "--fail-on",
        "warning",
    ]
)

assert arguments.target == Path("src")
assert arguments.output_format == "json"
assert arguments.fail_on == "warning"
```

`argv=None` kullanıldığında mevcut process argümanları ayrıştırılır.

#### Yardım çıktısı

Standart yardım seçenekleri desteklenir:

```powershell
securecode-analyzer --help
securecode-analyzer -h
```

CLI foundation şu aşamada:

- Analyzer oluşturmaz
- Dosya analizi çalıştırmaz
- Terminal bulgu çıktısı üretmez
- JSON çıktısı oluşturmaz
- Exit code politikası belirlemez

Bu sorumluluklar sonraki CLI bileşenlerinde ele alınacaktır.

#### Varsayılan kurallar

`create_default_rules()` aşağıdaki altı kuralı immutable bir tuple içinde
döndürür:

```python
rules = create_default_rules()
```

Kural sırası:

```text
SA001 - LongFunctionRule
SA002 - LongClassRule
SA003 - TodoFixmeRule
SA004 - EmptyExceptRule
SA005 - HardcodedSecretRule
SA006 - NamingConventionRule
```

Her çağrı yeni bir tuple ve yeni kural nesneleri üretir:

```python
first_rules = create_default_rules()
second_rules = create_default_rules()

assert first_rules is not second_rules
assert first_rules[0] is not second_rules[0]
```

`LongFunctionRule` ve `LongClassRule` kendi varsayılan eşik değerleriyle
oluşturulur.

#### Varsayılan analyzer

`create_default_analyzer()` aşağıdaki gerçek bileşenleri birbirine bağlar:

- `FileScanner`
- `SourceReader`
- `AnalysisEngine`
- `ProjectAnalyzer`
- Altı varsayılan analiz kuralı

Temel kullanım:

```python
from static_analyzer.default_factory import create_default_analyzer

analyzer = create_default_analyzer()
findings = analyzer.analyze("src")
```

Her çağrı bağımsız analyzer bileşenleri üretir:

```python
first_analyzer = create_default_analyzer()
second_analyzer = create_default_analyzer()

assert first_analyzer is not second_analyzer
assert first_analyzer.engine is not second_analyzer.engine
```

Factory yalnızca nesneleri oluşturur ve birbirine bağlar. Aşağıdaki işlemleri
gerçekleştirmez:

- Hedef klasörü doğrudan analiz etmek
- Dosya okumak
- AST oluşturmak
- Terminal veya JSON çıktısı üretmek
- Process exit code belirlemek
- CLI argümanlarını parse etmek
- Dependency veya CVE taraması yapmak

Factory tarafından oluşturulan analyzer, alt bileşenlerden gelen hataları
değiştirmeden çağıran katmana iletir.

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
- Varsayılan analiz bileşenlerini oluşturan factory geliştirildi.
- `create_default_rules()` fonksiyonu eklendi.
- `create_default_analyzer()` fonksiyonu eklendi.
- `SA001` ile `SA006` arasındaki altı kuralın kararlı sırada oluşturulması sağlandı.
- Varsayılan kuralların immutable tuple olarak döndürülmesi sağlandı.
- Her factory çağrısında bağımsız kural ve analyzer nesneleri oluşturulması sağlandı.
- `FileScanner`, `SourceReader`, `AnalysisEngine` ve `ProjectAnalyzer` bileşenlerinin otomatik bağlanması sağlandı.
- Factory tarafından oluşturulan analyzer uçtan uca test edildi.
- Default analyzer factory 16 test senaryosuyla doğrulandı.
- CLI argüman ayrıştırma temeli geliştirildi.
- Immutable ve slots kullanan `CliArguments` veri modeli eklendi.
- Yeni parser oluşturan `build_parser()` fonksiyonu eklendi.
- Doğrulanmış CLI verisi oluşturan `parse_arguments()` fonksiyonu eklendi.
- Zorunlu hedef klasör argümanı desteklendi.
- Hedef yolun `Path` nesnesine dönüştürülmesi sağlandı.
- `text` ve `json` çıktı formatları desteklendi.
- Varsayılan çıktı formatı `text` olarak belirlendi.
- Standart `argparse` yardım ve kullanım hatası davranışları korundu.
- CLI foundation 20 test senaryosuyla doğrulandı.
- Bulguları okunabilir terminal metnine dönüştüren text formatter geliştirildi.
- `format_findings_text()` public fonksiyonu eklendi.
- Severity, kural kimliği, dosya yolu, satır, sütun ve mesaj bilgilerinin gösterilmesi sağlandı.
- Sütun numarası bulunmayan bulguların desteklenmesi sağlandı.
- Tekil ve çoğul bulgu özetleri eklendi.
- Boş bulgu koleksiyonu için `No findings found.` çıktısı eklendi.
- Liste, tuple ve generator girdileri desteklendi.
- Bulguların giriş sırasının korunması sağlandı.
- Formatter çıktısının sonunda fazladan yeni satır bulunmaması sağlandı.
- Bulgu nesnelerinin değiştirilmemesi doğrulandı.
- Text formatter 22 test senaryosuyla doğrulandı.
- Bulguları makine tarafından okunabilir JSON metnine dönüştüren JSON formatter geliştirildi.
- `format_findings_json()` public fonksiyonu eklendi.
- Üst seviye `findings` ve `summary` alanları oluşturuldu.
- `summary.total` alanının gerçek bulgu sayısını içermesi sağlandı.
- Bulgu verilerinin `Finding.to_dict()` üzerinden oluşturulması sağlandı.
- Severity değerlerinin küçük harfli string olarak gösterilmesi sağlandı.
- Eksik sütun numaralarının JSON `null` olarak gösterilmesi sağlandı.
- İki boşluk girintili okunabilir JSON çıktısı eklendi.
- Unicode karakterlerin korunması sağlandı.
- Liste, tuple ve generator girdileri desteklendi.
- Bulguların giriş sırasının korunması sağlandı.
- JSON formatter 25 test senaryosuyla doğrulandı.
- CLI argümanlarını, analyzer factory'yi ve formatter bileşenlerini birleştiren CLI runner geliştirildi.
- `run_cli()` ve `main()` public fonksiyonları eklendi.
- Varsayılan ve açık text formatı desteği eklendi.
- JSON formatı desteği eklendi.
- Analyzer factory bağımlılığının testlerde değiştirilebilmesi sağlandı.
- Analyzer factory ve analyzer çağrılarının bir kez yapılması sağlandı.
- Başarılı çıktının standart çıktıya yazılması sağlandı.
- Çıktının sonuna tam olarak bir yeni satır eklenmesi sağlandı.
- Bulgusuz analiz için exit code `0` politikası eklendi.
- Bulgulu analiz için exit code `1` politikası eklendi.
- Operasyonel hatalar için exit code `2` politikası eklendi.
- Beklenen operasyonel hataların standart hata çıktısına yazılması sağlandı.
- Beklenmeyen exception türlerinin gizlenmemesi sağlandı.
- Standart argparse `SystemExit` davranışı korundu.
- `securecode-analyzer` console script girişi eklendi.
- CLI runner 29 test senaryosuyla doğrulandı.
- Projedeki toplam 288 test başarıyla çalıştırıldı.
- SecureCode Analyzer kendi `src` klasörü üzerinde çalıştırıldı.
- Text ve JSON self-analysis sonuçları karşılaştırıldı.
- Başlangıçta iki `SA001` Long Function bulgusu tespit edildi.
- İki bulgu da geçerli kod kalitesi problemi olarak sınıflandırıldı.
- Hardcoded secret kuralının `check()` fonksiyonu yardımcı metotlara ayrıldı.
- Naming convention kuralının `check()` fonksiyonu yardımcı metotlara ayrıldı.
- Kural eşikleri ve bulgu politikaları değiştirilmeden self-analysis bulguları giderildi.
- Son self-analysis sonucunda sıfır bulgu elde edildi.
- Text ve JSON exit code değerlerinin `0` olduğu doğrulandı.
- Self-analysis sonuçları ayrı bir raporda belgelendi.


Henüz tamamlanmayan çalışmalar:

- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- CI/CD entegrasyonu

## 17. Navigation

- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
