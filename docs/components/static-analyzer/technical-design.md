# Static Code Analyzer - Teknik Tasarım

## 1. Genel Yaklaşım

Static Code Analyzer, Python kaynak kodlarını çalıştırmadan inceleyerek temel
kod kalitesi ve güvenlik problemlerini tespit edecektir.

Bileşen iki farklı analiz yöntemini birlikte kullanacaktır:

- Python kodunun yapısal bölümlerini incelemek için Python'ın yerleşik
  `ast` modülü
- Metin tabanlı kontroller için satır taraması ve düzenli ifadeler (regex)

AST ve metin tabanlı analiz yöntemleri aynı probleme zorla uygulanmayacaktır.
Her kural için problemin yapısına en uygun yöntem seçilecektir.

## 2. Tasarım Hedefleri

Statik analiz aracının tasarımında aşağıdaki hedefler dikkate alınmaktadır:

- Analiz kurallarını birbirinden bağımsız tutmak
- Yeni kuralların mevcut kodu değiştirmeden eklenebilmesini sağlamak
- Python dosyalarını AST tabanlı kurallar için yalnızca bir kez parse etmek
- Bütün bulguları ortak bir veri modeliyle temsil etmek
- Kuralların ayrı ayrı test edilebilmesini sağlamak
- Terminal ve JSON çıktılarını destekleyebilecek bir yapı oluşturmak
- Bir dosyada hata oluştuğunda mümkünse diğer dosyaların analizine devam etmek
- CLI ve CI/CD kullanımına uygun exit code üretmek

## 3. Mevcut Proje Yapısı

Statik analiz bileşeninin mevcut dosya yapısı aşağıdaki gibidir:

```text
src/
└── static_analyzer/
    ├── __init__.py
    ├── analysis_engine.py
    ├── file_scanner.py
    ├── models.py
    ├── source_reader.py
    └── rules/
        ├── __init__.py
        ├── base.py
        ├── long_class.py
        └── long_function.py

tests/
├── test_analysis_engine.py
├── test_base_rule.py
├── test_file_scanner.py
├── test_long_class_rule.py
├── test_long_function_rule.py
├── test_models.py
└── test_source_reader.py
```

### 3.1 `static_analyzer.models`

Analiz aracı tarafından kullanılacak ortak veri yapılarını içerir.

Mevcut sorumlulukları:

- Desteklenen önem seviyelerini tanımlamak
- Tespit edilen problemleri `Finding` veri modeliyle temsil etmek
- Bulguları JSON formatına uygun sözlüklere dönüştürmek

### 3.2 `static_analyzer.rules.base`

AST tabanlı analiz kurallarının uygulaması gereken ortak arayüzü tanımlar.

### 3.3 `static_analyzer.rules`

Kural arayüzlerinin ve somut kural sınıflarının paket dışından düzenli şekilde
kullanılmasını sağlar.

### 3.4 `static_analyzer.rules.long_function`

Yapılandırılmış satır sınırını aşan normal ve asenkron fonksiyonları tespit
eden `LongFunctionRule` sınıfını içerir.

Bu yapı sayesinde aşağıdaki importlar kullanılabilir:

```python
from static_analyzer.rules import BaseRule, LongFunctionRule
```
### 3.5 `static_analyzer.rules.long_class`

Yapılandırılmış satır sınırını aşan Python sınıflarını tespit eden
`LongClassRule` sınıfını içerir.

Kural, normal ve iç içe sınıf tanımlarını `ast.ClassDef` düğümleri üzerinden
kontrol eder.

Bu yapı sayesinde aşağıdaki import kullanılabilir:

```python
from static_analyzer.rules import LongClassRule
```
### 3.6 `static_analyzer.file_scanner`

Kullanıcı tarafından verilen hedef dizin içerisindeki Python kaynak
dosyalarını bulmaktan sorumludur.

Modül aşağıdaki yapıları içerir:

- `DEFAULT_EXCLUDED_DIRECTORIES`
- `FileScanner`

`FileScanner`, hedef dizini ve alt klasörlerini tarar. Yalnızca `.py`
uzantılı dosyaları döndürür.

Varsayılan olarak aşağıdaki klasörleri tarama dışında bırakır:

```text
.git
.venv
__pycache__
```

Kullanıcı tarafından verilen özel klasör isimleri varsayılan hariç tutma
listesine eklenir.

Örnek kullanım:

```python
from static_analyzer.file_scanner import FileScanner

scanner = FileScanner()
python_files = scanner.scan("src")
```
### 3.7 `static_analyzer.source_reader`

Python kaynak dosyalarının UTF-8 olarak okunmasından ve AST yapısına
dönüştürülmesinden sorumludur.

Modül aşağıdaki yapıları içerir:

- `SourceFile`
- `SourceReader`

`SourceFile`, dosya yolu, kaynak kod metni ve oluşturulan AST yapısını aynı
değiştirilemez veri modelinde tutar.

Örnek kullanım:

```python
from static_analyzer.source_reader import SourceReader

reader = SourceReader()
source_file = reader.read("example.py")
```

### 3.8 `static_analyzer.analysis_engine`

Parse edilmiş kaynak dosya üzerinde kayıtlı analiz kurallarını çalıştıran
`AnalysisEngine` sınıfını içerir.

Temel sorumlulukları:

- Kuralları değiştirilemez bir `tuple` içerisinde saklamak
- Her kayıtlı kuralı yalnızca bir kez çalıştırmak
- `SourceFile` içerisindeki mevcut AST nesnesini yeniden kullanmak
- Gerçek kaynak dosya yolunu her kurala iletmek
- Kuralların ürettiği bulguları ortak bir listede birleştirmek
- Kural ve bulgu sırasını korumak
- Kural exception'larını gizlemeden çağıran katmana iletmek

Temel kullanım:

```python
from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.rules import LongClassRule, LongFunctionRule

engine = AnalysisEngine(
    rules=[
        LongFunctionRule(),
        LongClassRule(),
    ]
)

findings = engine.analyze(source_file)
```

Analiz motoru kaynak dosyayı okumaz ve kaynak kodu yeniden parse etmez.
Bu sorumluluk `SourceReader` bileşenine aittir.

Kurallar şu bilgilerle çalıştırılır:

```python
rule.check(
    source_file.tree,
    str(source_file.file_path),
)
```

Her kuralın döndürdüğü `Finding` nesneleri tek bir `list[Finding]`
içerisinde toplanır.

## 4. Analiz Akışı

Bileşenin mevcut ve planlanan çalışma sırası aşağıdaki şekildedir:

1. Kullanıcıdan analiz edilecek dosya veya klasör yolu alınır.
2. `FileScanner` analiz edilecek Python dosyalarını bulur.
3. `SourceReader` her kaynak dosyayı UTF-8 olarak okur.
4. Kaynak kod bir kez `ast.parse()` ile AST yapısına dönüştürülür.
5. `AnalysisEngine` kayıtlı AST tabanlı kuralları aynı AST nesnesi üzerinde
   çalıştırır.
6. Kuralların döndürdüğü `Finding` nesneleri ortak bir listede birleştirilir.
7. Planlanan metin tabanlı kurallar kaynak kod veya kaynak satırları üzerinde
   çalıştırılır.
8. Sonuçlar terminalde kullanıcıya gösterilir.
9. İstenirse sonuçlar JSON dosyasına yazılır.
10. Bulunan problemlere ve önem seviyesi eşiğine göre uygun exit code üretilir.

`SourceReader` tarafından oluşturulan AST, `AnalysisEngine` tarafından yeniden
kullanılır. Analiz motoru kaynak kodu tekrar parse etmez; böylece birden fazla
kural çalıştırıldığında gereksiz işlem tekrarı önlenir.

## 5. Analiz Kuralı Türleri

### 5.1 AST Tabanlı Kontroller

AST tabanlı analiz, kuralın Python sözdizimini veya kodun yapısal ilişkilerini
incelemesi gerektiğinde kullanılacaktır.

Uygulanan AST tabanlı kurallar:

- Uzun fonksiyon tespiti
- Uzun sınıf tespiti

Planlanan diğer AST tabanlı kurallar:

- Boş `except` bloğu tespiti
- Fonksiyon isimlendirme kontrolü
- Sınıf isimlendirme kontrolü

AST kullanılmasının temel nedeni, gerçek Python yapılarını yorum satırlarından
ve metin değerlerinden ayırabilmesidir.

Örneğin bir metin içerisinde geçen `except` kelimesi, gerçek bir exception
bloğu olarak değerlendirilmemelidir.

### 5.2 Metin Tabanlı Kontroller

Satır taraması veya regex, kontrol edilmek istenen bilginin AST içerisinde
anlamlı şekilde temsil edilmediği durumlarda kullanılacaktır.

Planlanan metin tabanlı kurallar:

- `TODO` ifadelerinin tespiti
- `FIXME` ifadelerinin tespiti
- Şüpheli hardcoded parola tespiti
- Şüpheli API anahtarı veya token tespiti
- Şüpheli bağlantı adresi tespiti

Hardcoded secret kontrolü yanlış pozitif sonuçlar üretebilir. Bu nedenle bu
kontrolün sonuçları doğrulanmış bir güvenlik açığı yerine şüpheli bulgu olarak
raporlanacaktır.

## 6. Bulgu Veri Modeli

Analiz sırasında tespit edilen bütün problemler ortak bir `Finding` veri
modeliyle temsil edilmektedir.

Mevcut `Finding` modeli aşağıdaki alanları içerir:

| Alan | Veri tipi | Açıklama |
|---|---|---|
| `rule_id` | `str` | Bulguyu oluşturan kuralın benzersiz kimliği |
| `message` | `str` | Tespit edilen problemin açıklaması |
| `file_path` | `str` | Analiz edilen kaynak dosyanın yolu |
| `line_number` | `int` | Problemin tespit edildiği satır |
| `severity` | `Severity` | Bulguların önem seviyesi |
| `column_number` | `int \| None` | Varsa problemin başladığı sütun |

Desteklenen önem seviyeleri:

- `INFO`
- `WARNING`
- `ERROR`

Varsayılan önem seviyesi `WARNING` olarak belirlenmiştir.

`Finding` veri modeli değiştirilemez (`frozen`) olarak tanımlanmıştır. Bu
sayede oluşturulan bir bulgunun analiz sürecinin ilerleyen aşamalarında
yanlışlıkla değiştirilmesi engellenir.

`Finding.to_dict()` metodu, bulguyu JSON formatına dönüştürmeye uygun bir
sözlük hâline getirir. `Severity` enum değeri sözlük içerisinde kendi metinsel
değeriyle saklanır.

Örnek:

```json
{
  "rule_id": "SA001",
  "message": "Fonksiyon belirlenen satır sınırını aşıyor.",
  "file_path": "example.py",
  "line_number": 10,
  "severity": "warning",
  "column_number": 0
}
```

Mevcut modelde problemin açıklaması `message` alanında tutulmaktadır.

Görev kapsamındaki çözüm önerisi ihtiyacı için ileride aşağıdaki
alternatiflerden biri değerlendirilecektir:

1. `Finding` modeline ayrı bir `suggestion` alanı eklemek
2. Çözüm önerisini `message` içerisinde göstermek
3. Kural metadata bilgilerinde ortak bir öneri tanımlamak

Bu karar, raporlama katmanı geliştirilirken ve çözüm önerilerinin çıktı
formatındaki yeri kesinleştirilirken tekrar değerlendirilecektir.

## 7. Kural Mimarisi

AST tabanlı analiz kuralları ortak bir `BaseRule` soyut sınıfını
uygulamaktadır.

Her kural aşağıdaki metadata bilgilerini tanımlamalıdır:

- `rule_id`: kuralın benzersiz kimliği
- `name`: kullanıcı tarafından okunabilir kural adı
- `description`: kuralın amacını açıklayan kısa metin

Her somut kural aşağıdaki `check()` metodunu uygulamak zorundadır:

```python
def check(self, tree: ast.AST, file_path: str) -> list[Finding]:
    ...
```

Metot aşağıdaki girdileri alır:

- Analiz edilen kaynak kodun AST yapısı
- Analiz edilen dosyanın yolu

Metot, kural tarafından tespit edilen bütün `Finding` nesnelerini liste
olarak döndürür.

### 7.1 Soyut Temel Sınıf Kullanımının Nedeni

Soyut temel sınıf kullanılması, bütün AST tabanlı kuralların aynı sözleşmeye
uymasını zorunlu hâle getirir.

Sınıf tabanlı yapı ileride aşağıdaki ihtiyaçların karşılanmasını
kolaylaştırır:

- Kural metadata bilgilerinin tutulması
- Varsayılan önem seviyelerinin tanımlanması
- Yapılandırılabilir eşik değerleri
- Kurala özel yapılandırmalar
- Ortak yardımcı metotlar

`BaseRule` sınıfı doğrudan kullanılamaz. Yalnızca `check()` metodunu uygulayan
somut kural sınıfları oluşturulabilir.

### 7.2 Değerlendirilen Alternatif

Her analiz kuralının bağımsız bir fonksiyon olarak tanımlanması da
değerlendirilmiştir.

Fonksiyon tabanlı yaklaşım daha az başlangıç kodu gerektirir. Ancak aşağıdaki
bilgilerin düzenli şekilde yönetilmesini zorlaştırabilir:

- Kural kimliği
- Kural adı
- Kural açıklaması
- Varsayılan önem seviyesi
- Yapılandırılabilir eşik değeri
- Kurala özel yardımcı metotlar

Bu nedenle ilk uygulama için sınıf tabanlı yaklaşım seçilmiştir.

### 7.3 Mevcut Tasarım Riski

Mevcut `BaseRule` arayüzü yalnızca AST yapısını ve dosya yolunu kabul
etmektedir.

Metin tabanlı kuralların kaynak kodun kendisine veya kaynak satırlarına
ihtiyaç duyması beklenmektedir.

Bu ihtiyaç ortaya çıktığında aşağıdaki alternatiflerden biri
değerlendirilecektir:

1. Metin tabanlı kurallar için ayrı bir temel sınıf oluşturmak
2. AST, kaynak kod, kaynak satırları ve dosya yolunu içeren ortak bir
   `AnalysisContext` veri modeli oluşturmak
3. Mevcut `BaseRule` arayüzünü genişletmek

Gerçek bir metin tabanlı kural geliştirilmeden arayüz gereksiz şekilde
genişletilmeyecektir.

### 7.4 `LongFunctionRule` Sınıf Tasarımı

İlk somut AST tabanlı analiz kuralı olarak `LongFunctionRule` uygulanmıştır.

Sınıf aşağıdaki dosyada bulunmaktadır:

```text
src/static_analyzer/rules/long_function.py
```

Sınıf, `BaseRule` soyut sınıfından kalıtım almaktadır:

```python
class LongFunctionRule(BaseRule):
    ...
```

### Sınıf Metadata Bilgileri

`LongFunctionRule` aşağıdaki metadata bilgilerini tanımlamaktadır:

| Alan | Değer |
|---|---|
| `rule_id` | `SA001` |
| `name` | `Long Function` |
| `description` | Yapılandırılmış satır sınırını aşan fonksiyonları tespit eden açıklama |

Bu bilgiler ileride terminal ve JSON raporlarında kullanılacaktır.

### Varsayılan Eşik Değeri

Kuralın varsayılan fonksiyon uzunluğu sınırı:

```python
DEFAULT_MAX_LINES = 50
```

Sabit değer modül seviyesinde tanımlanmıştır. Böylece varsayılan değer hem
sınıf içinde hem de testlerde açık biçimde görülebilecektir.

Kural oluşturulurken özel bir eşik değeri verilebilmektedir:

```python
rule = LongFunctionRule(max_lines=30)
```

Özel değer verilmezse `50` satırlık varsayılan sınır kullanılmaktadır.

### Constructor Tasarımı

Sınıfın constructor metodu aşağıdaki sorumluluklara sahiptir:

- `max_lines` değerini kabul etmek
- Değeri sınıf örneğinde saklamak
- Eşik değerinin pozitif bir tam sayı olmasını doğrulamak

Uygulanan imza:

```python
def __init__(self, max_lines: int = DEFAULT_MAX_LINES) -> None:
    ...
```

`max_lines` değeri pozitif bir tam sayı değilse `ValueError` üretilmektedir.

Bu doğrulama, anlamlı olmayan eşik değerleriyle analiz yapılmasını engeller.

### `check()` Metodu

Kural, `BaseRule` tarafından tanımlanan aşağıdaki sözleşmeyi uygulamaktadır:

```python
def check(self, tree: ast.AST, file_path: str) -> list[Finding]:
    ...
```

Metodun çalışma adımları:

1. Boş bir bulgu listesi oluşturulur.
2. AST düğümleri `ast.walk()` kullanılarak dolaşılır.
3. `ast.FunctionDef` ve `ast.AsyncFunctionDef` düğümleri seçilir.
4. Her fonksiyonun başlangıç ve bitiş satırları alınır.
5. Fonksiyonun toplam fiziksel satır sayısı hesaplanır.
6. Uzunluk yapılandırılmış eşik değerinden büyükse `Finding` oluşturulur.
7. Tespit edilen bütün bulgular liste olarak döndürülür.

### Fonksiyon Uzunluğu Hesabı

Fonksiyon uzunluğu aşağıdaki formülle hesaplanmaktadır:

```python
end_line = node.end_lineno or node.lineno
function_length = end_line - node.lineno + 1
```

`end_lineno` bilgisinin bulunmaması durumunda fonksiyon uzunluğu bir satır
olarak değerlendirilmektedir.

Karşılaştırma aşağıdaki şekilde yapılmaktadır:

```python
if function_length > self.max_lines:
    ...
```

Bu nedenle eşik değerine eşit fonksiyonlar bulgu üretmemektedir.

### Bulgu Oluşturma

Eşik değerini aşan her fonksiyon için aşağıdaki alanları içeren bir `Finding`
oluşturulmaktadır:

```python
Finding(
    rule_id=self.rule_id,
    message=message,
    file_path=file_path,
    line_number=node.lineno,
    column_number=node.col_offset,
    severity=Severity.WARNING,
)
```

Bulgu mesajı aşağıdaki biçimde oluşturulmaktadır:

```text
Function 'process_data' has 64 lines, exceeding the limit of 50.
```

Mesaj içerisinde aşağıdaki bilgiler bulunmaktadır:

- Fonksiyon adı
- Hesaplanan fonksiyon uzunluğu
- Yapılandırılmış eşik değeri

### Normal ve Asenkron Fonksiyon Desteği

Aşağıdaki iki AST düğümü aynı kuralla kontrol edilmektedir:

```python
(ast.FunctionDef, ast.AsyncFunctionDef)
```

Bu sayede hem `def` hem de `async def` ile tanımlanan fonksiyonlar
desteklenmektedir.

### İç İçe Fonksiyon Davranışı

`ast.walk()` bütün alt düğümleri dolaştığı için iç içe tanımlanan fonksiyonlar
ayrı ayrı kontrol edilmektedir.

Dış fonksiyonun uzunluğu, iç fonksiyona ait satırları da kapsayabilir. İç
fonksiyon ise kendi başlangıç ve bitiş satırları üzerinden ayrıca
değerlendirilmektedir.

Bu davranış ilk sürüm için kabul edilmektedir.

### Decorator Satırları

AST üzerindeki `FunctionDef.lineno` değeri genellikle `def` veya `async def`
satırını gösterir.

Fonksiyona ait decorator satırları ilk sürümde fonksiyon uzunluğu hesabına
eklenmemektedir.

Bu karar analiz dokümanındaki ilk sürüm kapsamıyla uyumludur.

### Public Export

Kural aşağıdaki dosya üzerinden dışa aktarılmaktadır:

```text
src/static_analyzer/rules/__init__.py
```

Kullanım:

```python
from static_analyzer.rules import LongFunctionRule
```

Bu sayede kullanıcı kodunun kuralın gerçek modül yoluna bağımlı olması
engellenmektedir.

### Unit Test Yapısı

Kural testleri aşağıdaki dosyada bulunmaktadır:

```text
tests/test_long_function_rule.py
```

Testlerde küçük Python kaynak kodları `ast.parse()` ile doğrudan AST yapısına
dönüştürülmektedir.

Uygulanan temel test grupları:

- Varsayılan eşik değerinin doğrulanması
- Özel eşik değerinin kullanılabilmesi
- Sıfır, negatif, boolean ve tam sayı olmayan eşiklerin reddedilmesi
- Kısa normal fonksiyonun bulgu üretmemesi
- Uzun normal fonksiyonun bulgu üretmesi
- Uzun asenkron fonksiyonun bulgu üretmesi
- Eşik değerine eşit fonksiyonun bulgu üretmemesi
- Birden fazla uzun fonksiyonun ayrı bulgular üretmesi
- İç içe fonksiyonların ayrı kontrol edilmesi
- Bulgu alanlarının doğru oluşturulması

### Değerlendirilen Alternatifler

Fonksiyonların yalnızca doğrudan AST gövdesinde aranması değerlendirilmiştir.
Bu yaklaşım iç içe fonksiyonları gözden kaçıracağı için tercih edilmemiştir.

Fonksiyon uzunluğunu hesaplamak için kaynak kod satırlarının ayrıca okunması da
değerlendirilmiştir. AST zaten başlangıç ve bitiş satırı bilgilerini sunduğu
için ilk sürümde ek bir kaynak kod işlemi yapılmamaktadır.

### Bilinen Sınırlamalar

İlk sürüm aşağıdaki sınırlamalara sahiptir:

- Boş satırlar uzunluğa dahil edilir.
- Yorum satırları uzunluğa dahil edilir.
- Docstring satırları uzunluğa dahil edilir.
- Decorator satırları uzunluğa dahil edilmez.
- Dış fonksiyonun uzunluğu iç fonksiyonun satırlarını da kapsayabilir.
- Fonksiyonun bilişsel veya döngüsel karmaşıklığı ölçülmez.
### 7.5 `LongClassRule` Sınıf Tasarımı

İkinci somut AST tabanlı analiz kuralı olarak `LongClassRule`
uygulanmıştır.

Sınıf aşağıdaki dosyada bulunmaktadır:

```text
src/static_analyzer/rules/long_class.py
```

Sınıf, `BaseRule` soyut sınıfından kalıtım almaktadır:

```python
class LongClassRule(BaseRule):
    ...
```

#### Kural Metadata Bilgileri

`LongClassRule` aşağıdaki metadata bilgilerini tanımlar:

| Alan | Değer |
|---|---|
| `rule_id` | `SA002` |
| `name` | `Long Class` |
| `description` | Yapılandırılmış satır sınırını aşan sınıfları tespit eden açıklama |

Bu bilgiler ileride terminal ve JSON raporlarında kullanılacaktır.

#### Varsayılan Eşik Değeri

Kuralın varsayılan sınıf uzunluğu sınırı:

```python
DEFAULT_MAX_CLASS_LINES = 200
```

Kural oluşturulurken özel bir eşik değeri verilebilir:

```python
rule = LongClassRule(max_lines=100)
```

Özel değer verilmezse 200 satırlık varsayılan sınır kullanılır.

#### Constructor Tasarımı

Constructor aşağıdaki sorumluluklara sahiptir:

- `max_lines` değerini kabul etmek
- Eşik değerini kural örneğinde saklamak
- Değerin pozitif bir tam sayı olduğunu doğrulamak

Uygulanan imza:

```python
def __init__(
    self,
    max_lines: int = DEFAULT_MAX_CLASS_LINES,
) -> None:
    ...
```

Aşağıdaki değerler geçersiz kabul edilir:

- `0`
- Negatif tam sayılar
- Boolean değerler
- Ondalıklı sayılar
- Tam sayı olmayan diğer değerler

Geçersiz eşik değerlerinde `ValueError` üretilir.

#### `check()` Metodu

Kural, `BaseRule` tarafından tanımlanan aşağıdaki sözleşmeyi uygular:

```python
def check(
    self,
    tree: ast.AST,
    file_path: str,
) -> list[Finding]:
    ...
```

Metodun çalışma sırası:

1. Boş bir bulgu listesi oluşturulur.
2. AST düğümleri `ast.walk()` ile dolaşılır.
3. `ast.ClassDef` düğümleri seçilir.
4. Her sınıfın başlangıç ve bitiş satırları alınır.
5. Sınıfın toplam fiziksel satır sayısı hesaplanır.
6. Uzunluk eşik değerinden büyükse `Finding` oluşturulur.
7. Bütün bulgular liste olarak döndürülür.

#### Sınıf Uzunluğu Hesabı

Sınıf uzunluğu aşağıdaki kodla hesaplanır:

```python
end_line = node.end_lineno or node.lineno
class_length = end_line - node.lineno + 1
```

`end_lineno` bulunmadığında `lineno` yedek değer olarak kullanılır.

Karşılaştırma davranışı:

```python
if class_length <= self.max_lines:
    continue
```

Bu nedenle:

- Eşik değerinden kısa sınıflar bulgu üretmez.
- Eşik değerine eşit sınıflar bulgu üretmez.
- Eşik değerinden uzun sınıflar bulgu üretir.

#### Bulgu Oluşturma

Eşik değerini aşan her sınıf için bir `Finding` nesnesi oluşturulur:

```python
Finding(
    rule_id=self.rule_id,
    message=message,
    file_path=file_path,
    line_number=node.lineno,
    column_number=node.col_offset,
    severity=Severity.WARNING,
)
```

Bulgu mesajı aşağıdaki biçimdedir:

```text
Class 'DataProcessor' has 241 lines, exceeding the limit of 200.
```

Mesaj içerisinde şunlar yer alır:

- Sınıf adı
- Hesaplanan sınıf uzunluğu
- Yapılandırılmış eşik değeri

#### İç İçe Sınıf Davranışı

AST düğümleri `ast.walk()` ile dolaşıldığı için iç içe sınıflar ayrı
`ast.ClassDef` düğümleri olarak kontrol edilir.

Dış sınıfın uzunluğu iç sınıfa ait satırları da kapsayabilir. İç sınıf ise
kendi başlangıç ve bitiş satırlarına göre ayrıca değerlendirilir.

Bu davranış ilk sürüm için kabul edilmektedir.

#### Decorator Satırları

`ClassDef.lineno` değeri genellikle `class` ifadesinin bulunduğu satırı
gösterir.

Sınıf decorator satırları ilk sürümde uzunluk hesabına dahil edilmez.

Bu davranış `LongFunctionRule` ile tutarlıdır.

#### Public Export

Kural aşağıdaki paket dosyası üzerinden dışa aktarılır:

```text
src/static_analyzer/rules/__init__.py
```

Kullanım:

```python
from static_analyzer.rules import LongClassRule
```

Bu yaklaşım kullanıcı kodunun doğrudan gerçek modül yoluna bağımlı olmasını
engeller.

#### Unit Test Yapısı

Kural testleri aşağıdaki dosyada bulunur:

```text
tests/test_long_class_rule.py
```

Testlerde küçük Python kaynak kodları `ast.parse()` ile AST yapısına
dönüştürülmektedir.

Test edilen temel davranışlar:

- Varsayılan 200 satır eşiğinin kullanılması
- Özel eşik değerinin kullanılabilmesi
- Geçersiz eşik değerlerinin reddedilmesi
- Eşik değerine eşit sınıfın kabul edilmesi
- Uzun sınıf için bulgu oluşturulması
- Birden fazla uzun sınıfın ayrı bulgular üretmesi
- İç içe sınıfların ayrı ayrı kontrol edilmesi
- Bulgu alanlarının doğru oluşturulması
- Bulgu mesajının doğru oluşturulması

#### Değerlendirilen Alternatifler

Sınıfların yalnızca AST ağacının en üst seviyesinde aranması
değerlendirilmiştir.

Bu yaklaşım iç içe sınıfları gözden kaçıracağı için tercih edilmemiştir.

Sınıf uzunluğunun kaynak kod satırları yeniden okunarak hesaplanması da
değerlendirilmiştir. AST başlangıç ve bitiş satırlarını sağladığı için ek
kaynak kod işleme yapılmamıştır.

#### Bilinen Sınırlamalar

İlk sürüm aşağıdaki sınırlamalara sahiptir:

- Boş satırlar sınıf uzunluğuna dahil edilir.
- Yorum satırları sınıf uzunluğuna dahil edilir.
- Docstring satırları sınıf uzunluğuna dahil edilir.
- Decorator satırları sınıf uzunluğuna dahil edilmez.
- Dış sınıfın uzunluğu iç sınıfın satırlarını kapsayabilir.
- Metot sayısı ölçülmez.
- Alan sayısı ölçülmez.
- Kalıtım derinliği ölçülmez.
- Sınıf bağlılığı veya uyumu ölçülmez.

## 8. Dosya Tarayıcı Tasarımı

### 8.1 Amaç

`FileScanner`, analiz edilecek Python kaynak dosyalarının keşfedilmesinden
sorumludur.

Dosya tarayıcı yalnızca dosya yollarını bulur. Dosya içeriğinin okunması,
AST oluşturulması ve analiz kurallarının çalıştırılması farklı bileşenlerin
sorumluluğundadır.

Bu sorumluluk ayrımı sayesinde dosya keşfi bağımsız şekilde test
edilebilmektedir.

### 8.2 Modül Konumu

Dosya tarayıcı aşağıdaki modülde bulunmaktadır:

```text
src/static_analyzer/file_scanner.py
```

Testleri ise aşağıdaki dosyada bulunmaktadır:

```text
tests/test_file_scanner.py
```

### 8.3 Varsayılan Hariç Tutmalar

Tarama sırasında aşağıdaki klasörler varsayılan olarak atlanmaktadır:

```python
DEFAULT_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
    }
)
```

`frozenset` kullanılmasının nedenleri:

- Varsayılan değerlerin yanlışlıkla değiştirilmesini engellemek
- Klasör adlarında hızlı üyelik kontrolü yapmak
- Güvenli varsayılanları açık biçimde tanımlamak

### 8.4 Constructor Tasarımı

`FileScanner`, kullanıcı tarafından özel hariç tutulacak klasör isimlerini
kabul edebilir.

Uygulanan constructor imzası:

```python
def __init__(
    self,
    excluded_directories: Iterable[str] | None = None,
) -> None:
    ...
```

Özel hariç tutmalar varsayılan değerlerin yerine geçmez. Varsayılan listeye
eklenir:

```python
custom_exclusions = frozenset(excluded_directories or ())
self.excluded_directories = (
    DEFAULT_EXCLUDED_DIRECTORIES | custom_exclusions
)
```

Bu davranış `.git`, `.venv` ve `__pycache__` gibi güvenli varsayılanların
yanlışlıkla kaldırılmasını engeller.

### 8.5 `scan()` Metodu

Tarama metodu aşağıdaki imzaya sahiptir:

```python
def scan(self, target: str | Path) -> list[Path]:
    ...
```

Metot hem `str` hem de `pathlib.Path` hedeflerini kabul eder.

Hedef değer ilk olarak `Path` nesnesine dönüştürülür:

```python
target_path = Path(target)
```

### 8.6 Hedef Doğrulaması

Tarama başlamadan önce hedef yol doğrulanır.

Hedef mevcut değilse:

```python
raise FileNotFoundError(
    f"Target path does not exist: {target_path}"
)
```

Hedef bir dizin değilse:

```python
raise NotADirectoryError(
    f"Target path is not a directory: {target_path}"
)
```

Bu hatalar dosya tarayıcı tarafından gizlenmez. İleride CLI katmanı bu
hataları kullanıcı tarafından anlaşılır terminal mesajlarına
dönüştürecektir.

### 8.7 Özyinelemeli Dizin Taraması

Alt klasörlerin taranması için Python standart kütüphanesindeki `os.walk()`
kullanılmaktadır:

```python
for current_root, directory_names, file_names in os.walk(
    target_path,
    followlinks=False,
):
    ...
```

`os.walk()` tercih edilmesinin nedenleri:

- Alt klasörleri özyinelemeli olarak dolaşabilmesi
- Taranacak alt klasör listesinin yerinde değiştirilebilmesi
- Sembolik bağlantı davranışının kontrol edilebilmesi
- Python standart kütüphanesinde bulunması

### 8.8 Hariç Tutulan Klasörlerin Budanması

`os.walk()` tarafından sağlanan `directory_names` listesi yerinde
değiştirilmektedir:

```python
directory_names[:] = sorted(
    directory_name
    for directory_name in directory_names
    if directory_name not in self.excluded_directories
    and not (
        current_directory / directory_name
    ).is_symlink()
)
```

Listenin yerinde değiştirilmesi önemlidir. Bu sayede `os.walk()` hariç
tutulan klasörlerin içine hiç girmez.

Klasörlerin yalnızca sonuç aşamasında filtrelenmesi tercih edilmemiştir.
Böyle bir yaklaşım gereksiz dosya sistemi taraması yapılmasına neden olurdu.

### 8.9 Sembolik Bağlantı Davranışı

`followlinks=False` kullanılarak sembolik bağlantılı dizinlerin takip
edilmemesi sağlanmaktadır.

Ek olarak alt klasör listesi oluşturulurken `is_symlink()` kontrolü
yapılmaktadır.

Bu karar aşağıdaki riskleri azaltır:

- Sonsuz dizin döngüleri
- Aynı dosyanın birden fazla kez bulunması
- Hedef dizinin dışındaki dosyalara geçilmesi

### 8.10 Python Dosyalarının Seçilmesi

Her dosyanın uzantısı `Path.suffix` ile kontrol edilir:

```python
if file_path.suffix == ".py":
    python_files.append(file_path)
```

Bu nedenle yalnızca tam olarak `.py` uzantısına sahip dosyalar sonuç
listesine eklenir.

Aşağıdaki dosyalar dikkate alınmaz:

```text
README.md
example.pyc
requirements.txt
config.json
```

### 8.11 Sıralı Sonuçlar

Bulunan dosyalar sıralanarak döndürülmektedir:

```python
return sorted(python_files)
```

Sıralı sonuçların sağladığı avantajlar:

- Testlerin deterministik olması
- Terminal ve JSON çıktılarının kararlı olması
- Farklı çalıştırmaların daha kolay karşılaştırılması
- İşletim sisteminden kaynaklanan dosya sırası farklılıklarının azaltılması

### 8.12 Çıktı Tipi

Metot aşağıdaki türde sonuç döndürür:

```python
list[Path]
```

Dosya bulunmaması hata değildir. Böyle bir durumda boş liste döndürülür:

```python
[]
```

### 8.13 Test Stratejisi

`FileScanner` için 12 test senaryosu hazırlanmıştır.

Testler `pytest` tarafından sağlanan `tmp_path` fixture'ını kullanır. Böylece
gerçek proje dizini değiştirilmeden geçici dosya yapıları oluşturulabilir.

Doğrulanan temel davranışlar:

- Varsayılan klasör hariç tutmalarının kullanılması
- Özel hariç tutmaların varsayılanlara eklenmesi
- Mevcut olmayan hedef yolun reddedilmesi
- Dosya olarak verilen hedefin reddedilmesi
- Boş dizin için boş liste döndürülmesi
- Kök dizindeki Python dosyalarının bulunması
- Alt klasörlerdeki Python dosyalarının bulunması
- Python olmayan dosyaların yok sayılması
- Varsayılan klasörlerin atlanması
- Özel klasörlerin atlanması
- Sonuçların sıralı olması
- Sonuçların `Path` nesnelerinden oluşması

### 8.14 Bilinen Sınırlamalar

İlk sürüm aşağıdaki işlemleri gerçekleştirmez:

- Dosya içeriğini okumak
- Dosya encoding bilgisini doğrulamak
- Python syntax doğrulaması yapmak
- AST oluşturmak
- Analiz kurallarını çalıştırmak
- Tek bir dosyayı doğrudan hedef olarak kabul etmek
- Büyük projeler için paralel tarama yapmak
- Dosya uzantısını büyük/küçük harf duyarsız değerlendirmek

Bu sorumluluklar ihtiyaç ortaya çıktığında ayrı geliştirme adımları olarak
ele alınacaktır.

## 9. Kaynak Kod Okuyucu Tasarımı

### 9.1 Amaç

`SourceReader`, `FileScanner` tarafından bulunan Python kaynak dosyalarının
okunmasından ve AST yapısına dönüştürülmesinden sorumludur.

Dosya keşfi, kaynak kod okuma ve analiz kurallarını çalıştırma sorumlulukları
ayrı bileşenlerde tutulmaktadır.

Bu ayrım sayesinde kaynak kod okuma ve parse etme davranışları bağımsız
şekilde test edilebilmektedir.

### 9.2 Modül Konumu

Kaynak kod okuyucu aşağıdaki modülde bulunmaktadır:

```text
src/static_analyzer/source_reader.py
```

Testleri aşağıdaki dosyada bulunmaktadır:

```text
tests/test_source_reader.py
```

### 9.3 `SourceFile` Veri Modeli

Okunan kaynak kod ve oluşturulan AST aynı veri modelinde tutulmaktadır:

```python
@dataclass(frozen=True, slots=True)
class SourceFile:
    file_path: Path
    source: str
    tree: ast.AST
```

Alanların sorumlulukları:

| Alan | Veri tipi | Açıklama |
|---|---|---|
| `file_path` | `Path` | Okunan kaynak dosyanın yolu |
| `source` | `str` | Dosyanın UTF-8 olarak okunan tam içeriği |
| `tree` | `ast.AST` | Kaynak koddan oluşturulan AST yapısı |

`frozen=True` kullanılması sonuç nesnesinin sonradan yanlışlıkla
değiştirilmesini engeller.

`slots=True` kullanılması veri modelinin yalnızca tanımlanan alanları
saklamasını sağlar.

### 9.4 `SourceReader` Sınıfı

`SourceReader`, kaynak dosyayı okuyan ve parse eden `read()` metodunu içerir.

```python
class SourceReader:
    def read(self, target: str | Path) -> SourceFile:
        ...
```

Metot hem `str` hem de `pathlib.Path` dosya yollarını kabul eder.

Hedef yol ilk olarak `Path` nesnesine dönüştürülür:

```python
file_path = Path(target)
```

### 9.5 Hedef Dosya Doğrulaması

Kaynak dosya okunmadan önce hedef yol doğrulanır.

Hedef mevcut değilse:

```python
raise FileNotFoundError(
    f"Source file does not exist: {file_path}"
)
```

Hedef bir dizinse:

```python
raise IsADirectoryError(
    f"Source path is a directory: {file_path}"
)
```

Bu hatalar kaynak kod okuyucu tarafından gizlenmez. Üst seviye koordinasyon
veya CLI katmanı ileride bu hataları kullanıcı dostu mesajlara dönüştürecektir.

### 9.6 UTF-8 Kaynak Kod Okuma

Kaynak dosya açıkça UTF-8 encoding kullanılarak okunur:

```python
source = file_path.read_text(encoding="utf-8")
```

Encoding değerinin açıkça belirtilmesi işletim sisteminin varsayılan encoding
değerine bağımlılığı azaltır.

UTF-8 olmayan bir dosyada oluşan `UnicodeDecodeError` gizlenmez.

### 9.7 AST Oluşturma

Okunan kaynak kod Python standart kütüphanesindeki `ast.parse()` fonksiyonuna
gönderilir:

```python
tree = ast.parse(
    source,
    filename=str(file_path),
)
```

Dosya yolunun `filename` parametresine verilmesinin nedeni, oluşabilecek
`SyntaxError` nesnesinde gerçek dosya yolunun bulunmasını sağlamaktır.

Kaynak dosya her `read()` çağrısında yalnızca bir kez parse edilir.

Bu sayede aynı dosyanın her analiz kuralı için yeniden parse edilmesi
engellenmektedir.

### 9.8 Syntax Hatası Davranışı

Kaynak kod geçerli Python sözdizimine sahip değilse `ast.parse()`
`SyntaxError` üretir.

İlk sürümde bu hata:

- Gizlenmez
- `Finding` nesnesine dönüştürülmez
- Boş AST ile değiştirilmez

Üst seviye koordinasyon veya CLI katmanı syntax hatası bulunan dosyayı
raporlayarak diğer dosyaların analizine devam edebilir.

### 9.9 Sonuç Oluşturma

Kaynak kod başarıyla okunduğunda ve parse edildiğinde bir `SourceFile` nesnesi
döndürülür:

```python
return SourceFile(
    file_path=file_path,
    source=source,
    tree=tree,
)
```

Bu yapı sayesinde sonraki bileşenler aynı dosya için:

- Dosya yoluna
- Kaynak kod metnine
- AST yapısına

aynı nesne üzerinden erişebilir.

### 9.10 Analiz Akışındaki Konumu

Kaynak kod okuyucu analiz akışında `FileScanner` ile analiz motoru arasında
yer alır:

```text
FileScanner
    ↓
SourceReader
    ↓
Analysis Engine
    ↓
Rules
    ↓
Findings
```

`FileScanner` yalnızca dosya yollarını bulur.

`SourceReader` her dosyayı okur ve AST yapısını oluşturur.

Analiz motoru ise oluşturulan `SourceFile` nesnesini analiz kurallarına
gönderir.

### 9.11 Test Stratejisi

`SourceReader` için 11 test senaryosu hazırlanmıştır.

Testlerde `pytest` tarafından sağlanan `tmp_path` ve `monkeypatch`
fixture'ları kullanılmaktadır.

Doğrulanan temel davranışlar:

- Geçerli Python dosyasından `SourceFile` oluşturulması
- `str` dosya yolunun kabul edilmesi
- `Path` dosya yolunun kabul edilmesi
- Dosya yolunun `Path` olarak saklanması
- Kaynak kod metninin değiştirilmeden korunması
- AST yapısının kaynak kodu temsil etmesi
- Mevcut olmayan dosyanın reddedilmesi
- Dizin hedefinin reddedilmesi
- Geçersiz Python kodunda `SyntaxError` üretilmesi
- Syntax hatasında gerçek dosya yolunun bulunması
- UTF-8 olmayan dosyada `UnicodeDecodeError` üretilmesi
- Kaynak kodun yalnızca bir kez parse edilmesi

`ast.parse()` çağrı sayısını doğrulamak için test içerisinde `monkeypatch`
kullanılmaktadır.

### 9.12 Bilinen Sınırlamalar

İlk sürüm aşağıdaki işlemleri yapmaz:

- Klasör taramak
- Dosya uzantısını doğrulamak
- Encoding tahmini yapmak
- Syntax hatasını kullanıcı dostu rapora dönüştürmek
- AST analiz kurallarını çalıştırmak
- Bulgu üretmek
- Terminal veya JSON çıktısı oluşturmak
- Aynı dosya için AST önbelleği tutmak

Bu sorumluluklar üst seviye koordinasyon, raporlama ve CLI katmanlarında
ele alınacaktır.

## 10. Analiz Motoru Tasarımı

### 10.1 Amaç

`AnalysisEngine`, `SourceReader` tarafından oluşturulan `SourceFile` nesnesi
üzerinde kayıtlı analiz kurallarını çalıştırmaktan sorumludur.

Motor, kaynak dosyayı tekrar okumaz ve kaynak kodu tekrar parse etmez. Hazır AST
nesnesini kullanarak bütün kural sonuçlarını ortak bir bulgu listesinde toplar.

### 10.2 Modül Konumu

Analiz motoru aşağıdaki modülde bulunmaktadır:

```text
src/static_analyzer/analysis_engine.py
```

Testleri aşağıdaki dosyada bulunmaktadır:

```text
tests/test_analysis_engine.py
```

### 10.3 Constructor Tasarımı

Constructor, `BaseRule` örneklerinden oluşan herhangi bir iterable kabul eder:

```python
def __init__(
    self,
    rules: Iterable[BaseRule],
) -> None:
    self.rules = tuple(rules)
```

Kuralların `tuple` içerisinde saklanması, motor oluşturulduktan sonra kural
koleksiyonunun yanlışlıkla değiştirilmesini engeller.

Generator gibi tek kullanımlık iterable değerler de constructor sırasında
tüketilerek kararlı bir kural koleksiyonuna dönüştürülür.

Boş bir kural koleksiyonu geçerlidir. Bu durumda analiz sonucu boş listedir.

### 10.4 `analyze()` Metodu

Analiz metodu bir `SourceFile` kabul eder ve birleşik bulgu listesini döndürür:

```python
def analyze(
    self,
    source_file: SourceFile,
) -> list[Finding]:
    ...
```

Metot aşağıdaki çalışma sırasını uygular:

1. Boş bir `Finding` listesi oluşturur.
2. Kayıtlı kuralları constructor'a verildikleri sırayla dolaşır.
3. Her kuralın `check()` metodunu yalnızca bir kez çağırır.
4. Aynı AST nesnesini ve gerçek dosya yolunu kurala iletir.
5. Kuralın döndürdüğü bulguları ortak listeye ekler.
6. Birleştirilmiş bulgu listesini döndürür.

### 10.5 Kural Çağrısı

Her kural aşağıdaki bilgilerle çalıştırılır:

```python
rule_findings = rule.check(
    source_file.tree,
    str(source_file.file_path),
)
```

`source_file.tree` doğrudan kullanıldığı için kaynak kod yeniden parse edilmez.

Dosya yolu `str` biçiminde gönderilir. Bu davranış mevcut `BaseRule.check()`
sözleşmesiyle uyumludur.

### 10.6 Bulguların Birleştirilmesi

Her kural sıfır, bir veya birden fazla `Finding` döndürebilir.

Sonuçlar aşağıdaki işlemle tek listede birleştirilir:

```python
findings.extend(rule_findings)
```

Bulgu sırası deterministiktir:

1. Kuralların motora verildiği sıra korunur.
2. Her kuralın kendi içerisinde döndürdüğü bulgu sırası korunur.

Analiz motoru ilk sürümde bulguları yeniden sıralamaz.

### 10.7 Hata Davranışı

Bir kural beklenmeyen exception üretirse analiz motoru bu hatayı sessizce
gizlemez.

Exception çağıran katmana iletilir. Böylece hata davranışı görünür ve test
edilebilir kalır.

Bir kural hatasından sonra diğer dosyaların analizine devam etme sorumluluğu
ileride geliştirilecek üst seviye koordinasyon veya CLI katmanına aittir.

### 10.8 Sorumluluk Sınırları

`AnalysisEngine` aşağıdaki işlemleri gerçekleştirmez:

- Klasör taramak
- Python dosyalarını bulmak
- Kaynak dosyayı okumak
- Kaynak kodu parse etmek
- AST oluşturmak
- Terminal çıktısı üretmek
- JSON raporu oluşturmak
- Exit code belirlemek
- Dosya okuma veya syntax hatalarını kullanıcı dostu rapora dönüştürmek

Bu sorumluluklar `FileScanner`, `SourceReader`, raporlama ve CLI
bileşenlerine ayrılmıştır.

### 10.9 Test Stratejisi

`AnalysisEngine` için 12 test senaryosu hazırlanmıştır.

Doğrulanan temel davranışlar:

- Kuralların `tuple` olarak saklanması
- Boş kural koleksiyonunun boş sonuç döndürmesi
- Tek kuralın yalnızca bir kez çalıştırılması
- Birden fazla kuralın ayrı ayrı ve yalnızca bir kez çalıştırılması
- Aynı AST nesnesinin bütün kurallara iletilmesi
- Gerçek dosya yolunun `str` olarak kurallara iletilmesi
- Kaynak kodun yeniden parse edilmemesi
- Tek bulgunun döndürülmesi
- Bir kuralın birden fazla bulgusunun korunması
- Kural ve bulgu sırasının korunması
- Bulgusuz kuralın boş sonuç üretmesi
- Kural exception'ının gizlenmemesi

### 10.10 Bilinen Sınırlamalar

İlk sürümde analiz motoru:

- Kuralları çalışma anında ekleyip kaldırmaz
- Bulguları önem seviyesine veya dosya konumuna göre sıralamaz
- Kural exception'larını bulguya dönüştürmez
- Bir kural hatasından sonra aynı dosyadaki diğer kurallara devam etmez
- Birden fazla dosyanın analizini koordine etmez
- Paralel kural çalıştırma yapmaz

Bu ihtiyaçlar üst seviye analiz koordinasyonu ve CLI tasarımı geliştirilirken
yeniden değerlendirilecektir.

## 11. Hata Yönetimi

Aşağıdaki durumlar kontrollü şekilde yönetilecektir:

- Dosyanın bulunamaması
- Dosyanın okunamaması
- Geçersiz Python sözdizimi
- Desteklenmeyen dosya türü
- Boş klasör verilmesi
- Geçersiz klasör yolu verilmesi
- Kaynak dosyanın UTF-8 olarak okunamaması
- Analiz kuralının beklenmeyen hata üretmesi

Bir dosyada hata oluşması durumunda kullanıcıya anlaşılır bir hata mesajı
gösterilecektir.

Mümkün olduğu durumlarda bir dosyadaki hata diğer dosyaların analizini
durdurmayacaktır.

Dosya okuma ve sözdizimi hataları, kod kalitesi bulgularından ayrı şekilde
raporlanacaktır.

## 12. Test Stratejisi

Projede otomatik testler için `pytest` kullanılmaktadır.

Mevcut unit testler aşağıdaki davranışları doğrulamaktadır:

- `Finding.to_dict()` metodunun serileştirilebilir veri döndürmesi
- `Finding` modelinin varsayılan olarak `WARNING` önem seviyesini kullanması
- Soyut `BaseRule` sınıfının doğrudan oluşturulamaması
- Somut bir kuralın `check()` sözleşmesini uygulayabilmesi
- `LongFunctionRule` sınıfının varsayılan eşiği kullanması
- Geçersiz fonksiyon eşik değerlerinin reddedilmesi
- Eşik değerine eşit fonksiyonların kabul edilmesi
- Uzun normal ve asenkron fonksiyonların tespit edilmesi
- Birden fazla ve iç içe fonksiyonun ayrı ayrı kontrol edilmesi
- `SA001` bulgu alanlarının doğru üretilmesi
- `LongClassRule` sınıfının varsayılan eşiği kullanması
- Özel sınıf uzunluğu eşiğinin kullanılabilmesi
- Geçersiz sınıf eşiklerinin reddedilmesi
- Eşik değerine eşit sınıfların kabul edilmesi
- Uzun sınıfların tespit edilmesi
- Birden fazla ve iç içe sınıfın ayrı ayrı kontrol edilmesi
- `SA002` bulgu alanlarının doğru üretilmesi
- `FileScanner` sınıfının varsayılan hariç tutmaları kullanması
- Özel hariç tutmaların varsayılan listeye eklenmesi
- Geçersiz hedef yolların reddedilmesi
- Alt klasörlerdeki Python dosyalarının bulunması
- Python olmayan dosyaların yok sayılması
- Hariç tutulan klasörlerin taranmaması
- Tarama sonuçlarının sıralı `Path` nesneleri olması
- `SourceReader` sınıfının `str` ve `Path` girdileriyle çalışması
- Python kaynak kodunun UTF-8 olarak okunması
- Kaynak kod metninin değiştirilmeden korunması
- AST yapısının doğru oluşturulması
- Mevcut olmayan dosyanın reddedilmesi
- Dizin hedefinin reddedilmesi
- Syntax ve encoding hatalarının gizlenmemesi
- Syntax hatasında gerçek dosya yolunun gösterilmesi
- Kaynak kodun yalnızca bir kez parse edilmesi
- `AnalysisEngine` kurallarının `tuple` içerisinde saklanması
- Boş kural koleksiyonunun boş sonuç döndürmesi
- Her kayıtlı kuralın yalnızca bir kez çalıştırılması
- Aynı AST nesnesi ve gerçek dosya yolunun kurallara iletilmesi
- Birden fazla kuralın bulgularının sıralı şekilde birleştirilmesi
- Kaynak kodun analiz motorunda yeniden parse edilmemesi
- Kural exception'larının gizlenmemesi

Bütün testler aşağıdaki komutla çalıştırılabilir:

```bash
python -m pytest -v
```

Mevcut durumda toplam 59 unit test bulunmaktadır.

- 10 test `LongFunctionRule` davranışlarını doğrulamaktadır.
- 10 test `LongClassRule` davranışlarını doğrulamaktadır.
- 12 test `FileScanner` davranışlarını doğrulamaktadır.
- 11 test `SourceReader` davranışlarını doğrulamaktadır.
- 12 test `AnalysisEngine` davranışlarını doğrulamaktadır.
- 4 test ortak veri modeli ve temel kural arayüzünü doğrulamaktadır.

Bütün testler başarılı şekilde çalışmaktadır.

Her yeni analiz kuralı için en az aşağıdaki senaryolar test edilecektir:

- Bulgu oluşturması gereken kaynak kod
- Bulgu oluşturmaması gereken kaynak kod
- Doğru kural kimliğinin üretilmesi
- Doğru dosya yolunun üretilmesi
- Doğru satır numarasının üretilmesi
- Doğru önem seviyesinin üretilmesi
- Varsa yapılandırılabilir eşik değerinin davranışı
- Kurala özgü sınır durumları

Testlerde analiz edilmek istenen küçük Python kodları `ast.parse()` ile
doğrudan AST yapısına dönüştürülmektedir. Böylece testler için gereksiz
geçici dosyalar oluşturulması önlenecektir.

## 13. Geliştirme ve Paketleme Yapısı

Proje yapılandırması `pyproject.toml` dosyasında tutulmaktadır.

Mevcut yapılandırma aşağıdaki sorumluluklara sahiptir:

- Paketleme sistemi olarak `setuptools` kullanmak
- Python paketlerini `src` klasörü altında bulmak
- Desteklenen en düşük Python sürümünü tanımlamak
- Geliştirme bağımlılığı olarak `pytest` paketini tanımlamak
- Pytest test klasörünü `tests` olarak belirlemek

Proje geliştirme ortamına editable olarak kurulmaktadır:

```bash
python -m pip install -e ".[dev]"
```

Editable kurulum sayesinde `src` klasörü altındaki kod değişiklikleri için
paketin her seferinde yeniden kurulmasına gerek kalmaz.

Yerel geliştirme bağımlılıkları `.venv` sanal ortamında tutulur. Sanal ortam,
önbellekler ve paketleme çıktıları `.gitignore` ile Git takibinin dışında
bırakılır.

## 14. Prototip ve Kalıcı Mimariye Geçiş

İlk AST prototipi aşağıdaki teknik kararları doğrulamak amacıyla
hazırlanmıştır:

- Python dosyasının UTF-8 olarak okunabilmesi
- Kaynak kodun `ast.parse()` ile parse edilebilmesi
- Normal ve asenkron fonksiyonların AST içerisinde bulunabilmesi
- Fonksiyon başlangıç ve bitiş satırlarının hesaplanabilmesi
- Uzun fonksiyonların belirlenen eşik değerine göre tespit edilebilmesi

Prototip, kalıcı proje mimarisinin bir parçası olarak kullanılmamıştır.

Prototip kodundaki uzun fonksiyon tespiti `LongFunctionRule` sınıfına,
kaynak kod okuma ve parse etme `SourceReader` bileşenine, kural koordinasyonu
ise `AnalysisEngine` sınıfına taşınmıştır. Kalan sorumluluklar raporlama ve
CLI katmanlarına ayrılacaktır.

Böylece tek dosyada bulunan deneme kodu yerine test edilebilir ve
genişletilebilir modüler bir yapı oluşturulacaktır.

## 15. Mevcut Uygulama Durumu

Tamamlanan çalışmalar:

- Python paket yapısının oluşturulması
- `Severity` enum yapısının oluşturulması
- `Finding` veri modelinin oluşturulması
- Bulgular için sözlük serileştirmesinin oluşturulması
- Soyut `BaseRule` arayüzünün oluşturulması
- `BaseRule` arayüzünün paket üzerinden dışa aktarılması
- Veri modeli unit testlerinin hazırlanması
- Kural arayüzü unit testlerinin hazırlanması
- `pyproject.toml` yapılandırmasının hazırlanması
- Geliştirme bağımlılıklarının tanımlanması
- `.gitignore` dosyasının hazırlanması
- Sanal geliştirme ortamının kurulması
- `LongFunctionRule` sınıfının geliştirilmesi
- Varsayılan 50 satır fonksiyon eşiğinin tanımlanması
- Özel fonksiyon eşik değeri desteğinin eklenmesi
- Geçersiz fonksiyon eşik değerlerinin reddedilmesi
- Normal ve asenkron fonksiyon desteğinin eklenmesi
- İç içe fonksiyonların ayrı ayrı kontrol edilmesi
- `LongFunctionRule` sınıfının public paket üzerinden dışa aktarılması
- Uzun fonksiyon kuralı için 10 test senaryosunun hazırlanması
- `LongClassRule` sınıfının geliştirilmesi
- Varsayılan 200 satır sınıf eşiğinin tanımlanması
- Özel sınıf eşik değeri desteğinin eklenmesi
- Geçersiz sınıf eşik değerlerinin reddedilmesi
- İç içe sınıfların ayrı ayrı kontrol edilmesi
- `LongClassRule` sınıfının public paket üzerinden dışa aktarılması
- Uzun sınıf kuralı için 10 test senaryosunun hazırlanması
- `FileScanner` sınıfının geliştirilmesi
- Hedef dizin doğrulamasının eklenmesi
- Alt klasörlerdeki Python dosyalarının bulunması
- Varsayılan klasör hariç tutmalarının tanımlanması
- Özel klasör hariç tutma desteğinin eklenmesi
- Sembolik bağlantılı dizinlerin takip edilmemesi
- Sonuçların sıralı `Path` nesneleri olarak döndürülmesi
- Dosya tarayıcı için 12 test senaryosunun hazırlanması
- `SourceFile` veri modelinin geliştirilmesi
- `SourceReader` sınıfının geliştirilmesi
- Python kaynak dosyalarının UTF-8 olarak okunması
- Kaynak kodun `ast.parse()` ile AST yapısına dönüştürülmesi
- AST oluşturulurken gerçek dosya yolunun kullanılması
- Syntax hatalarının gizlenmeden iletilmesi
- UTF-8 encoding hatalarının gizlenmeden iletilmesi
- Kaynak kodun yalnızca bir kez parse edilmesi
- Kaynak kod okuyucu için 11 test senaryosunun hazırlanması
- `AnalysisEngine` sınıfının geliştirilmesi
- Analiz kurallarının değiştirilemez bir `tuple` içerisinde saklanması
- Kayıtlı kuralların aynı AST nesnesi üzerinde çalıştırılması
- Gerçek kaynak dosya yolunun kurallara iletilmesi
- Birden fazla kuralın bulgularının ortak listede birleştirilmesi
- Kural ve bulgu sırasının korunması
- Kaynak kodun analiz motorunda yeniden parse edilmemesi
- Kural exception'larının gizlenmeden iletilmesi
- Analiz motoru için 12 test senaryosunun hazırlanması
- Projedeki toplam 59 testin başarıyla çalıştırılması

Henüz tamamlanmayan çalışmalar:

- Kural kayıt mekanizması
- Diğer analiz kuralları
- Metin tabanlı kural arayüzü
- Terminal çıktı biçimlendiricisi
- JSON çıktı katmanı
- CLI komutları
- Exit code politikası
- Aracın kendi kaynak kodunu analiz etmesi
- CI/CD entegrasyonu

## 16. Gelecek Geliştirmeler

Planlanan sonraki geliştirmeler:

- TODO/FIXME kuralının geliştirilmesi
- Boş `except` kuralının geliştirilmesi
- İsimlendirme kurallarının geliştirilmesi
- Hardcoded secret kuralının geliştirilmesi
- Yapılandırılabilir kural sınırları
- Terminal raporu
- JSON raporu
- Komut satırı parametreleri
- Önem seviyesi eşiklerinin belirlenmesi
- Analiz sonuçlarına göre exit code üretilmesi
- Statik analiz aracının kendi kaynak kodu üzerinde çalıştırılması
- GitHub Actions entegrasyonu

## 17. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Analiz ve Gereksinimler](analysis.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
