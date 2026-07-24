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
    ├── models.py
    └── rules/
        ├── __init__.py
        ├── base.py
        ├── long_class.py
        └── long_function.py

tests/
├── test_base_rule.py
├── test_long_class_rule.py
├── test_long_function_rule.py
└── test_models.py
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

## 4. Analiz Akışı

Bileşenin planlanan temel çalışma sırası aşağıdaki şekilde olacaktır:

1. Kullanıcıdan analiz edilecek dosya veya klasör yolu alınır.
2. Analiz edilmesi gereken Python dosyaları bulunur.
3. Her dosyanın içeriği UTF-8 formatında okunur.
4. Kaynak kod `ast.parse()` kullanılarak AST yapısına dönüştürülür.
5. Oluşturulan AST, kayıtlı AST tabanlı kurallara gönderilir.
6. Metin tabanlı kurallar, kaynak kod veya kaynak kod satırları üzerinde
   çalıştırılır.
7. Kuralların döndürdüğü `Finding` nesneleri ortak bir listede toplanır.
8. Sonuçlar terminalde kullanıcıya gösterilir.
9. İstenirse sonuçlar JSON dosyasına yazılır.
10. Bulunan problemlere ve önem seviyesi eşiğine göre uygun exit code üretilir.

Bir Python dosyasının her AST kuralı için tekrar parse edilmesi yerine dosyanın
bir kez parse edilmesi planlanmaktadır. Böylece birden fazla kural
çalıştırıldığında gereksiz işlem tekrarı önlenecektir.

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

## 8. Hata Yönetimi

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

## 9. Test Stratejisi
- `LongClassRule` sınıfının varsayılan eşiği kullanması
- Özel sınıf uzunluğu eşiğinin kullanılabilmesi
- Geçersiz sınıf eşiklerinin reddedilmesi
- Eşik değerine eşit sınıfların kabul edilmesi
- Uzun sınıfların tespit edilmesi
- Birden fazla ve iç içe sınıfın ayrı ayrı kontrol edilmesi
- `SA002` bulgu alanlarının doğru üretilmesi

Projede otomatik testler için `pytest` kullanılmaktadır.

Mevcut unit testler aşağıdaki davranışları doğrulamaktadır:

- `Finding.to_dict()` metodunun serileştirilebilir veri döndürmesi
- `Finding` modelinin varsayılan olarak `WARNING` önem seviyesini kullanması
- Soyut `BaseRule` sınıfının doğrudan oluşturulamaması
- Somut bir kuralın `check()` sözleşmesini uygulayabilmesi
- `LongFunctionRule` sınıfının varsayılan eşiği kullanması
- Geçersiz eşik değerlerinin reddedilmesi
- Eşik değerine eşit fonksiyonların kabul edilmesi
- Uzun normal ve asenkron fonksiyonların tespit edilmesi
- Birden fazla ve iç içe fonksiyonun ayrı ayrı kontrol edilmesi
- Bulgu alanlarının doğru üretilmesi

Bütün testler aşağıdaki komutla çalıştırılabilir:

```bash
python -m pytest -v
```

Mevcut durumda toplam 24 unit test bulunmaktadır.

- 10 test `LongFunctionRule` davranışlarını doğrulamaktadır.
- 10 test `LongClassRule` davranışlarını doğrulamaktadır.
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

## 10. Geliştirme ve Paketleme Yapısı

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

## 11. Prototip ve Kalıcı Mimariye Geçiş

İlk AST prototipi aşağıdaki teknik kararları doğrulamak amacıyla
hazırlanmıştır:

- Python dosyasının UTF-8 olarak okunabilmesi
- Kaynak kodun `ast.parse()` ile parse edilebilmesi
- Normal ve asenkron fonksiyonların AST içerisinde bulunabilmesi
- Fonksiyon başlangıç ve bitiş satırlarının hesaplanabilmesi
- Uzun fonksiyonların belirlenen eşik değerine göre tespit edilebilmesi

Prototip, kalıcı proje mimarisinin bir parçası olarak kullanılmamıştır.

Prototip kodundaki uzun fonksiyon tespiti sorumluluğu
`LongFunctionRule` sınıfına taşınmıştır. Kalan sorumluluklar analiz motoruna
ve çıktı katmanına ayrılacaktır.

Böylece tek dosyada bulunan deneme kodu yerine test edilebilir ve
genişletilebilir modüler bir yapı oluşturulacaktır.

## 12. Mevcut Uygulama Durumu

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
- Varsayılan 50 satır eşiğinin tanımlanması
- Özel eşik değeri desteğinin eklenmesi
- Geçersiz eşik değerlerinin reddedilmesi
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
- Projedeki toplam 24 testin başarıyla çalıştırılması

Henüz tamamlanmayan çalışmalar:

- Dosya bulma ve klasör tarama mekanizması
- Kaynak kod okuma ve parse etme servisi
- Analiz motoru
- Kural kayıt mekanizması
- Diğer analiz kuralları
- Metin tabanlı kural arayüzü
- Terminal çıktı biçimlendiricisi
- JSON çıktı katmanı
- CLI komutları
- Exit code politikası
- Aracın kendi kaynak kodunu analiz etmesi
- CI/CD entegrasyonu

## 13. Gelecek Geliştirmeler

Planlanan sonraki geliştirmeler:

- Klasör ve alt klasör taraması
- Birden fazla analiz kuralının birlikte çalıştırılması
- Yapılandırılabilir kural sınırları
- Terminal raporu
- JSON raporu
- Komut satırı parametreleri
- Önem seviyesi eşiklerinin belirlenmesi
- Analiz sonuçlarına göre exit code üretilmesi
- Statik analiz aracının kendi kaynak kodu üzerinde çalıştırılması
- GitHub Actions entegrasyonu

## 14. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Analiz ve Gereksinimler](analysis.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)