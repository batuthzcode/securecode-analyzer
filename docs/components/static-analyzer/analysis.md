# Static Code Analyzer - Analiz

## 1. Amaç

Static Code Analyzer bileşeninin amacı, Python kaynak kodlarını çalıştırmadan
inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit etmektir.

Araç, tespit ettiği problemlerin doğrudan hata olduğunu iddia etmek yerine
geliştirici tarafından incelenmesi gereken bulgular üretir.

## 2. Kapsam
Bileşenin temel kapsamı aşağıdaki işlemleri içerir:

- Tek bir Python dosyasını analiz etmek
- Bir klasör altındaki Python dosyalarını analiz etmek
- AST tabanlı kod kalite kurallarını çalıştırmak
- Metin tabanlı kontrolleri çalıştırmak
- Tespit edilen problemleri ortak bir bulgu modeliyle temsil etmek
- Bulguları terminalde göstermek
- Bulguları JSON formatında dışa aktarabilmek
- Analiz sonucuna göre uygun exit code üretmek

İlk sürümün amacı SonarQube gibi kapsamlı bir analiz platformu oluşturmak
değildir. Amaç, statik analiz sürecinin temel mantığını gösteren çalışan ve
genişletilebilir bir PoC hazırlamaktır.

## 3. Girdiler

Bileşen aşağıdaki girdileri kabul edecektir:

- Tek bir Python dosyasının yolu
- Bir Python proje klasörünün yolu
- Yapılandırılabilir kural eşikleri
- İsteğe bağlı çıktı formatı
- İsteğe bağlı çıktı dosyası

İlk aşamada yalnızca `.py` uzantılı dosyalar analiz edilecektir.

## 4. Fonksiyonel Gereksinimler

Statik analiz aracı aşağıdaki fonksiyonel gereksinimleri karşılamalıdır:

1. Kullanıcıdan dosya veya klasör yolu alabilmelidir.
2. Verilen klasör içindeki Python dosyalarını bulabilmelidir.
3. Python kaynak kodunu UTF-8 formatında okuyabilmelidir.
4. Kaynak kodu `ast.parse()` ile AST yapısına dönüştürebilmelidir.
5. Kayıtlı analiz kurallarını çalıştırabilmelidir.
6. Her kuralın ürettiği bulguları ortak bir listede toplayabilmelidir.
7. Bulguları terminalde gösterebilmelidir.
8. Bulguları JSON formatına dönüştürebilmelidir.
9. Dosya okuma ve sözdizimi hatalarını kontrollü şekilde yönetebilmelidir.
10. Yapılandırılan önem seviyesi eşiğine göre uygun exit code
    üretebilmelidir.
11. Aynı dosyada birden fazla bulgu üretebilmelidir.
12. Bir dosyadaki hata mümkünse diğer dosyaların analizini durdurmamalıdır.

## 5. Analiz Kuralları

| Kural | Durum | Yaklaşım | Gerekçe |
|---|---|---|---|
| Uzun fonksiyon | Uygulandı | AST | Fonksiyon başlangıç ve bitiş satırları yapısal olarak incelenir |
| Uzun sınıf | Uygulandı | AST | Sınıf başlangıç ve bitiş satırları yapısal olarak incelenir |
| Boş `except` bloğu | Planlandı | AST | Gerçek exception blokları incelenmelidir |
| Fonksiyon isimlendirme | Planlandı | AST | Fonksiyon tanımlarının isimleri kontrol edilir |
| Sınıf isimlendirme | Planlandı | AST | Sınıf tanımlarının isimleri kontrol edilir |
| `TODO` ve `FIXME` | Planlandı | Satır taraması | Yorumlar AST içerisinde doğrudan korunmaz |
| Hardcoded secret | Planlandı | Regex ve metin analizi | Şüpheli anahtar ve değer desenleri aranır |
| Bağlantı adresi | Planlandı | Regex ve metin analizi | Kaynak kod içerisindeki bağlantı desenleri aranır |

AST tabanlı kontroller, yorum veya string içerisindeki ifadeleri gerçek Python
yapılarıyla karıştırmamak için kullanılacaktır.

Metin tabanlı kontroller yanlış pozitif sonuçlar üretebilir. Özellikle
hardcoded secret bulguları doğrulanmış güvenlik açığı olarak değil, şüpheli
durum olarak raporlanacaktır.

## 6. Uzun Fonksiyon Kuralı

### 6.1 Amaç

Uzun fonksiyon kuralının amacı; okunması, test edilmesi ve bakımı
zorlaşabilecek fonksiyonları tespit etmektir.

Bir fonksiyonun uzun olması tek başına kesin bir hata değildir. Bu nedenle
kural, kodun hatalı olduğunu söylemek yerine geliştirici tarafından
incelenmesi gereken bir kod kalitesi bulgusu üretir.

### 6.2 Kural Bilgileri

Kural kimliği:

```text
SA001
```

Kural adı:

```text
Long Function
```

Varsayılan önem seviyesi:

```text
WARNING
```

### 6.3 Analiz Yöntemi

Kural Python'ın yerleşik `ast` modülünü kullanır.

AST tercih edilmesinin nedenleri:

- Gerçek fonksiyon tanımlarının güvenilir şekilde bulunabilmesi
- Normal ve asenkron fonksiyonların tespit edilebilmesi
- Yorum veya string içerisindeki `def` ifadelerinin dikkate alınmaması
- Fonksiyonların başlangıç ve bitiş satırlarının alınabilmesi
- İç içe tanımlanan fonksiyonların ayrı ayrı incelenebilmesi

Kural aşağıdaki AST düğümlerini kontrol eder:

- `ast.FunctionDef`
- `ast.AsyncFunctionDef`

### 6.4 Fonksiyon Uzunluğu Hesaplaması

Fonksiyon uzunluğu aşağıdaki AST bilgileri kullanılarak hesaplanır:

- `lineno`: fonksiyon tanımının başladığı satır
- `end_lineno`: fonksiyon tanımının bittiği satır

```text
fonksiyon uzunluğu = bitiş satırı - başlangıç satırı + 1
```

`end_lineno` bilgisinin bulunmadığı durumda başlangıç satırı kullanılır.

İlk sürümde başlangıç ve bitiş satırları arasındaki toplam fiziksel satır
sayısı dikkate alınır.

### 6.5 Varsayılan Eşik Değeri

Varsayılan eşik:

```text
50 satır
```

Fonksiyon uzunluğu eşik değerinden büyük olduğunda bulgu üretilir.

- 49 satırlık fonksiyon bulgu üretmez.
- 50 satırlık fonksiyon bulgu üretmez.
- 51 satırlık fonksiyon bulgu üretir.

Kural oluşturulurken özel bir eşik değeri verilebilir.

### 6.6 Eşik Doğrulaması

`max_lines` değeri pozitif bir tam sayı olmalıdır.

Aşağıdaki değerler reddedilir:

- `0`
- Negatif tam sayılar
- `True` ve `False`
- Ondalıklı sayılar
- Tam sayı olmayan diğer değerler

Geçersiz değerlerde `ValueError` üretilir.

### 6.7 Üretilecek Bulgu

Kural, eşik değerini aşan her fonksiyon için bir `Finding` nesnesi döndürür.

| Alan | Değer |
|---|---|
| `rule_id` | `SA001` |
| `message` | Fonksiyon adı, mevcut uzunluk ve izin verilen eşik |
| `file_path` | Analiz edilen dosyanın yolu |
| `line_number` | Fonksiyonun başladığı satır |
| `column_number` | AST düğümündeki `col_offset` değeri |
| `severity` | `WARNING` |

Örnek mesaj:

```text
Function 'process_data' has 64 lines, exceeding the limit of 50.
```

### 6.8 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamaktadır:

1. Normal Python fonksiyonlarını tespit eder.
2. Asenkron Python fonksiyonlarını tespit eder.
3. Eşik değerini aşan fonksiyon için bulgu üretir.
4. Eşik değerine eşit veya daha kısa fonksiyon için bulgu üretmez.
5. Özel bir eşik değeriyle çalışır.
6. Geçersiz eşik değerlerini reddeder.
7. Bulgunun kural kimliği `SA001` olur.
8. Bulgunun önem seviyesi `WARNING` olur.
9. Bulgunun dosya yolu, satır numarası ve sütun numarası doğru olur.
10. Birden fazla ve iç içe fonksiyon ayrı ayrı kontrol edilir.

### 6.9 Test Senaryoları

`LongFunctionRule` aşağıdaki senaryolarla doğrulanmıştır:

- Varsayılan eşik değeri
- Sıfır ve negatif eşik değerleri
- Boolean eşik değerleri
- Ondalıklı eşik değerleri
- Eşik değerine eşit fonksiyon
- Uzun normal fonksiyon
- Uzun asenkron fonksiyon
- Birden fazla uzun fonksiyon
- İç içe fonksiyonlar
- Bulgu alanları ve mesaj içeriği
## 7. Uzun Sınıf Kuralı

### 7.1 Amaç

Uzun sınıf kuralının amacı; çok fazla sorumluluk üstlenmiş olabilecek,
okunması, test edilmesi ve bakımı zorlaşan sınıfları tespit etmektir.

Bir sınıfın uzun olması tek başına kesin bir kod hatası değildir. Bu nedenle
kural, geliştirici tarafından incelenmesi gereken bir kod kalitesi bulgusu
üretir.

### 7.2 Kural Bilgileri

Kural kimliği:

```text
SA002
```

Kural adı:

```text
Long Class
```

Varsayılan önem seviyesi:

```text
WARNING
```

### 7.3 Analiz Yöntemi

Kural Python'ın yerleşik `ast` modülünü kullanır.

AST tercih edilmesinin nedenleri:

- Gerçek sınıf tanımlarının güvenilir şekilde bulunabilmesi
- Yorum veya string içerisindeki `class` ifadelerinin dikkate alınmaması
- Sınıfların başlangıç ve bitiş satırlarının alınabilmesi
- İç içe tanımlanan sınıfların ayrı ayrı incelenebilmesi
- Metotların ait oldukları sınıf yapısı içerisinde değerlendirilmesi

Kural aşağıdaki AST düğümünü kontrol eder:

```python
ast.ClassDef
```

### 7.4 Sınıf Uzunluğu Hesaplaması

Sınıf uzunluğu aşağıdaki AST bilgileri kullanılarak hesaplanır:

- `lineno`: sınıf tanımının başladığı satır
- `end_lineno`: sınıf tanımının bittiği satır

```text
sınıf uzunluğu = bitiş satırı - başlangıç satırı + 1
```

Uygulanan Python hesabı:

```python
end_line = node.end_lineno or node.lineno
class_length = end_line - node.lineno + 1
```

`end_lineno` bilgisinin bulunmadığı durumda başlangıç satırı yedek değer olarak
kullanılır.

İlk sürümde başlangıç ve bitiş satırları arasındaki toplam fiziksel satır
sayısı dikkate alınır.

### 7.5 Varsayılan Eşik Değeri

Varsayılan sınıf uzunluğu sınırı:

```text
200 satır
```

Sınıf uzunluğu eşik değerinden büyük olduğunda bulgu üretilir.

- 199 satırlık sınıf bulgu üretmez.
- 200 satırlık sınıf bulgu üretmez.
- 201 satırlık sınıf bulgu üretir.

Kural oluşturulurken özel bir eşik değeri verilebilir:

```python
rule = LongClassRule(max_lines=100)
```

### 7.6 Eşik Doğrulaması

`max_lines` değeri pozitif bir tam sayı olmalıdır.

Aşağıdaki değerler reddedilir:

- `0`
- Negatif tam sayılar
- `True` ve `False`
- Ondalıklı sayılar
- Tam sayı olmayan diğer değerler

Geçersiz değerlerde `ValueError` üretilir.

### 7.7 Üretilecek Bulgu

Kural, eşik değerini aşan her sınıf için bir `Finding` nesnesi döndürür.

| Alan | Değer |
|---|---|
| `rule_id` | `SA002` |
| `message` | Sınıf adı, mevcut uzunluk ve izin verilen eşik |
| `file_path` | Analiz edilen dosyanın yolu |
| `line_number` | Sınıfın başladığı satır |
| `column_number` | AST düğümündeki `col_offset` değeri |
| `severity` | `WARNING` |

Örnek mesaj:

```text
Class 'DataProcessor' has 241 lines, exceeding the limit of 200.
```

### 7.8 İç İçe Sınıf Davranışı

AST düğümleri `ast.walk()` ile dolaşılır.

Bu nedenle iç içe tanımlanan sınıflar ayrı AST düğümleri olarak kontrol
edilir.

Dış sınıfın uzunluğu iç sınıfa ait satırları kapsayabilir. İç sınıf ise kendi
başlangıç ve bitiş satırları üzerinden ayrıca değerlendirilir.

Bu davranış ilk sürüm için kabul edilmektedir.

### 7.9 Decorator Satırları

AST üzerindeki `ClassDef.lineno` değeri genellikle `class` satırını gösterir.

Sınıfa ait decorator satırları ilk sürümde sınıf uzunluğu hesabına dahil
edilmez.

Bu davranış `LongFunctionRule` ile tutarlıdır.

### 7.10 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamaktadır:

1. Python sınıf tanımlarını tespit eder.
2. Eşik değerini aşan sınıf için bulgu üretir.
3. Eşik değerine eşit sınıf için bulgu üretmez.
4. Eşik değerinden kısa sınıf için bulgu üretmez.
5. Varsayılan eşik değeri 200'dür.
6. Özel bir eşik değeriyle çalışır.
7. Geçersiz eşik değerlerini reddeder.
8. Bulgunun kural kimliği `SA002` olur.
9. Bulgunun önem seviyesi `WARNING` olur.
10. Dosya yolu, satır numarası ve sütun numarası doğru olur.
11. Birden fazla uzun sınıf için ayrı bulgular oluşturur.
12. İç içe sınıfları ayrı ayrı kontrol eder.
13. Bulgu mesajında sınıf adı bulunur.
14. Bulgu mesajında hesaplanan sınıf uzunluğu bulunur.
15. Bulgu mesajında yapılandırılmış eşik değeri bulunur.

### 7.11 Test Senaryoları

`LongClassRule` aşağıdaki senaryolarla doğrulanmıştır:

- Varsayılan 200 satır eşik değeri
- Özel eşik değerinin kullanılması
- Sıfır eşik değerinin reddedilmesi
- Negatif eşik değerinin reddedilmesi
- Boolean eşik değerinin reddedilmesi
- Ondalıklı eşik değerinin reddedilmesi
- Eşik değerinden kısa sınıf
- Eşik değerine eşit sınıf
- Eşik değerini aşan sınıf
- Birden fazla uzun sınıf
- İç içe sınıflar
- Bulgu alanları ve mesaj içeriği

### 7.12 İlk Sürüm Kapsamı Dışındaki Durumlar

İlk sürümde aşağıdaki ölçümler yapılmaz:

- Sınıf içerisindeki metot sayısı
- Sınıf içerisindeki alan sayısı
- Sınıfın kalıtım derinliği
- Sınıfın bağımlılık sayısı
- Sınıfın bağlılık veya uyum seviyesi
- Bilişsel karmaşıklık
- Yalnızca çalıştırılabilir satırların sayılması
## 8. Çıktı Gereksinimleri

Her bulgu için aşağıdaki bilgilerin üretilmesi beklenmektedir:

- Kural kimliği
- Kural adı
- Dosya yolu
- Satır numarası
- Varsa sütun numarası
- Önem seviyesi
- Problem açıklaması
- Çözüm önerisi

Mevcut `Finding` modelinde `rule_id`, `message`, `file_path`, `line_number`,
`severity` ve `column_number` alanları bulunmaktadır.

Kural adı ve çözüm önerisinin hangi katmanda tutulacağı, raporlama bileşeni
geliştirilirken netleştirilecektir.

## 9. Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır hata mesajlarıyla bildirilmelidir:

- Dosyanın bulunamaması
- Dosyanın okunamaması
- Geçersiz dosya uzantısı verilmesi
- Python sözdizimi hatası bulunması
- Geçersiz dosya veya klasör yolu verilmesi
- Boş klasör verilmesi
- Kaynak dosyanın UTF-8 olarak okunamaması
- Analiz kuralının beklenmeyen hata üretmesi

## 10. Fonksiyonel Olmayan Gereksinimler

### 10.1 Genişletilebilirlik

Yeni analiz kuralları mevcut kurallar değiştirilmeden eklenebilmelidir.

### 10.2 Test Edilebilirlik

Her analiz kuralı bağımsız unit testlerle doğrulanabilmelidir.

### 10.3 Okunabilirlik

Kod, anlaşılır sınıf ve fonksiyon isimleriyle geliştirilmelidir. Kamuya açık
sınıf ve fonksiyonlar açıklayıcı docstring içermelidir.

### 10.4 Güvenlik

Analiz edilen kaynak kod çalıştırılmamalıdır. Kaynak kod yalnızca metin ve AST
yapısı üzerinden incelenmelidir.

### 10.5 Taşınabilirlik

Araç Windows, Linux ve macOS ortamlarında çalışabilecek şekilde
geliştirilmelidir.

### 10.6 Performans

Her Python dosyası AST tabanlı kurallar için mümkün olduğunca yalnızca bir kez
parse edilmelidir.

## 11. Mevcut Durum

Tamamlanan çalışmalar:

- Statik analiz paket yapısı oluşturuldu.
- `Severity` enum yapısı oluşturuldu.
- `Finding` veri modeli oluşturuldu.
- Bulguların sözlük formatına dönüştürülmesi sağlandı.
- AST tabanlı kurallar için `BaseRule` arayüzü oluşturuldu.
- `LongFunctionRule` sınıfı geliştirildi.
- Normal ve asenkron fonksiyon desteği eklendi.
- İç içe fonksiyonların ayrı ayrı kontrol edilmesi sağlandı.
- Yapılandırılabilir fonksiyon uzunluğu sınırı eklendi.
- `LongClassRule` sınıfı geliştirildi.
- Yapılandırılabilir sınıf uzunluğu sınırı eklendi.
- İç içe sınıfların ayrı ayrı kontrol edilmesi sağlandı.
- Geçersiz eşik değerleri için doğrulama eklendi.
- Uzun fonksiyon kuralı 10 test senaryosuyla doğrulandı.
- Uzun sınıf kuralı 10 test senaryosuyla doğrulandı.
- `SourceFile` veri modeli geliştirildi.
- `SourceReader` sınıfı geliştirildi.
- Python kaynak dosyalarının UTF-8 olarak okunması sağlandı.
- Kaynak kodun `ast.parse()` ile AST yapısına dönüştürülmesi sağlandı.
- AST oluşturulurken gerçek dosya yolunun kullanılması sağlandı.
- Syntax hatalarının gizlenmeden iletilmesi sağlandı.
- UTF-8 encoding hatalarının gizlenmeden iletilmesi sağlandı.
- Kaynak dosyalarının yalnızca bir kez parse edilmesi sağlandı.
- Kaynak kod okuyucu 11 test senaryosuyla doğrulandı.
- Projenin toplam 47 testi başarılı şekilde çalışmaktadır.

Henüz tamamlanmayan çalışmalar:

- Analiz motoru
- TODO/FIXME kuralı
- Boş `except` kuralı
- İsimlendirme kuralları
- Hardcoded secret kuralı
- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- Aracın kendi kaynak kodunu analiz etmesi
- CI/CD entegrasyonu

## 12. Dosya Tarayıcı Gereksinimleri

### 12.1 Amaç

Dosya tarayıcı, kullanıcı tarafından verilen hedef dizin içerisindeki Python
kaynak dosyalarını bulmakla sorumludur.

Tarayıcı yalnızca dosya keşfi yapacaktır. Dosya içeriğini okuma, kaynak kodu
parse etme ve analiz kurallarını çalıştırma sorumlulukları sonraki
bileşenlerde ele alınacaktır.

Bu ayrım sayesinde dosya keşfi ve kaynak kod analizi birbirinden bağımsız
olarak test edilebilir.

### 12.2 Girdi

Tarayıcı hedef dizini aşağıdaki veri tiplerinden biriyle kabul edebilmelidir:

```python
str | pathlib.Path
```

Örnek:

```python
scanner.scan("src")
```

veya:

```python
scanner.scan(Path("src"))
```

### 12.3 Hedef Dizin Doğrulaması

Tarayıcı analiz başlamadan önce hedef yolu doğrulamalıdır.

Aşağıdaki davranışlar uygulanacaktır:

- Hedef yol mevcut değilse `FileNotFoundError` üretilmesi
- Hedef yol bir dizin değilse `NotADirectoryError` üretilmesi
- Geçerli bir dizin verilirse taramanın başlatılması

Hatalar sessizce yok sayılmayacaktır. Böylece CLI katmanı ileride kullanıcıya
anlaşılır bir hata mesajı gösterebilecektir.

### 12.4 Python Dosyalarının Bulunması

Tarayıcı hedef dizin içerisindeki `.py` uzantılı dosyaları bulmalıdır.

Arama aşağıdaki kapsamı içermelidir:

- Hedef dizinin doğrudan içerisindeki Python dosyaları
- Hedef dizinin alt klasörlerindeki Python dosyaları
- Birden fazla klasör seviyesindeki Python dosyaları

Python uzantısı taşımayan dosyalar sonuç listesine dahil edilmemelidir.

Örnek olarak aşağıdaki dosyalar dikkate alınmaz:

```text
README.md
requirements.txt
config.json
example.pyc
```

### 12.5 Varsayılan Hariç Tutulan Dizinler

Aşağıdaki dizinler varsayılan olarak tarama dışında bırakılmalıdır:

```text
.git
.venv
__pycache__
```

Bu dizinlerin içindeki `.py` dosyaları sonuç listesine eklenmemelidir.

Hariç tutulan dizinler alt klasörleriyle birlikte tarama dışında
bırakılmalıdır.

### 12.6 Özel Hariç Tutma Desteği

Kullanıcı varsayılan dizinlere ek olarak özel klasör adları verebilmelidir.

Örnek:

```python
scanner = FileScanner(
    excluded_directories={"generated", "vendor"},
)
```

Özel dizinler varsayılan hariç tutma listesine eklenmelidir. Varsayılan
güvenli hariç tutmalar kaldırılmamalıdır.

### 12.7 Çıktı

Tarama sonucunda Python dosyalarının `pathlib.Path` nesnelerinden oluşan bir
listesi döndürülmelidir:

```python
list[Path]
```

Sonuç listesi aynı dosya yapısı için her çalıştırmada aynı sırada olmalıdır.

Bu nedenle dosya yolları sıralanarak döndürülmelidir.

Hiç Python dosyası bulunmaması hata değildir. Bu durumda boş liste
döndürülmelidir:

```python
[]
```

### 12.8 Sembolik Bağlantılar

İlk sürümde sembolik bağlantı olarak tanımlanan dizinler takip
edilmeyecektir.

Bu karar aşağıdaki riskleri azaltır:

- Sonsuz klasör döngüleri
- Aynı dosyanın birden fazla kez bulunması
- Hedef dizinin dışındaki dosyaların yanlışlıkla taranması

### 12.9 Sorumluluk Sınırları

Dosya tarayıcı ilk sürümde aşağıdaki işlemleri yapmayacaktır:

- Dosya içeriğini okumak
- UTF-8 doğrulaması yapmak
- Python sözdizimini doğrulamak
- AST oluşturmak
- Analiz kurallarını çalıştırmak
- Bulgu üretmek
- Terminal veya JSON çıktısı oluşturmak

Bu sorumluluklar kaynak kod okuyucu, analiz motoru ve raporlama katmanlarında
ele alınacaktır.

### 12.10 Kabul Kriterleri

Dosya tarayıcı aşağıdaki koşulları sağlamalıdır:

1. Geçerli bir hedef dizini kabul eder.
2. `str` ve `Path` girdileriyle çalışır.
3. Hedef dizindeki `.py` dosyalarını bulur.
4. Alt klasörlerdeki `.py` dosyalarını bulur.
5. Python olmayan dosyaları dikkate almaz.
6. `.git` dizinini tarama dışında bırakır.
7. `.venv` dizinini tarama dışında bırakır.
8. `__pycache__` dizinini tarama dışında bırakır.
9. Özel olarak belirtilen klasörleri tarama dışında bırakır.
10. Sonuçları sıralı şekilde döndürür.
11. Sonuçları `Path` nesneleri olarak döndürür.
12. Python dosyası olmayan dizin için boş liste döndürür.
13. Mevcut olmayan hedef için `FileNotFoundError` üretir.
14. Dosya olarak verilen hedef için `NotADirectoryError` üretir.
15. Sembolik bağlantı dizinlerini takip etmez.

### 12.11 Planlanan Test Senaryoları

Dosya tarayıcı için aşağıdaki testler hazırlanacaktır:

- Varsayılan hariç tutulan dizinlerin doğrulanması
- Özel hariç tutulan dizinlerin saklanması
- Mevcut olmayan hedef yol
- Hedef yolun dosya olması
- Boş dizin taraması
- Kök dizindeki Python dosyasının bulunması
- Alt klasörlerdeki Python dosyalarının bulunması
- Python olmayan dosyaların yok sayılması
- Varsayılan hariç tutulan klasörlerin atlanması
- Özel hariç tutulan klasörlerin atlanması
- Sonuçların sıralı döndürülmesi
- Sonuçların `Path` nesnelerinden oluşması
## 13. Kaynak Kod Okuyucu Gereksinimleri

### 13.1 Amaç

Kaynak kod okuyucu, `FileScanner` tarafından bulunan Python dosyalarının
içeriğini okumak ve AST yapısına dönüştürmekle sorumludur.

Dosya keşfi, kaynak kod okuma ve analiz kurallarını çalıştırma sorumlulukları
ayrı bileşenlerde tutulacaktır.

Bu ayrım sayesinde kaynak kod okuma ve parse etme davranışları bağımsız
şekilde test edilebilir.

### 13.2 Girdi

Kaynak kod okuyucu hem `str` hem de `pathlib.Path` dosya yollarını kabul
etmelidir:

```python
str | pathlib.Path
```

Örnek kullanımlar:

```python
reader.read("example.py")
```

```python
reader.read(Path("example.py"))
```

### 13.3 Kaynak Kodun Okunması

Python kaynak dosyaları UTF-8 encoding kullanılarak okunmalıdır:

```python
source = file_path.read_text(encoding="utf-8")
```

Okunan kaynak kod herhangi bir değişiklik yapılmadan sonuç nesnesinde
saklanmalıdır.

### 13.4 AST Oluşturulması

Okunan Python kaynak kodu `ast.parse()` kullanılarak AST yapısına
dönüştürülmelidir:

```python
tree = ast.parse(
    source,
    filename=str(file_path),
)
```

Dosya yolunun `filename` parametresine verilmesi, syntax hata mesajlarında
gerçek dosya yolunun görünmesini sağlar.

Kaynak dosya her okuma işleminde yalnızca bir kez parse edilmelidir.

### 13.5 Hedef Dosya Doğrulaması

Kaynak kod okuyucu dosyayı okumadan önce hedef yolu doğrulamalıdır.

Aşağıdaki davranışlar uygulanmalıdır:

- Dosya yolu mevcut değilse `FileNotFoundError` üretilmesi
- Hedef yol bir dizinse `IsADirectoryError` üretilmesi
- Geçerli bir dosya verilirse okuma ve parse işleminin devam etmesi

### 13.6 Syntax Hataları

Geçersiz Python sözdizimi `ast.parse()` tarafından `SyntaxError` olarak
raporlanmalıdır.

İlk sürümde `SyntaxError`:

- Gizlenmemelidir.
- Boş bir AST ile değiştirilmemelidir.
- Kod kalitesi bulgusuna dönüştürülmemelidir.

Analiz motoru ileride bu hatayı kaydederek diğer dosyaların analizine devam
edecektir.

### 13.7 Encoding Hataları

UTF-8 olmayan kaynak dosyalarında oluşan `UnicodeDecodeError`
gizlenmemelidir.

Encoding tahmini yapılmayacaktır. Kaynak dosyaların UTF-8 olması
beklenmektedir.

### 13.8 Çıktı Modeli

Okunan kaynak kod ve oluşturulan AST aynı sonuç nesnesinde tutulmalıdır:

```python
@dataclass(frozen=True, slots=True)
class SourceFile:
    file_path: Path
    source: str
    tree: ast.AST
```

Alanların sorumlulukları:

| Alan | Açıklama |
|---|---|
| `file_path` | Okunan dosyanın `Path` biçimindeki yolu |
| `source` | Dosyanın UTF-8 olarak okunan tam içeriği |
| `tree` | Kaynak koddan oluşturulan AST yapısı |

Bu yapı sayesinde analiz kuralları dosyayı tekrar okumadan ve tekrar parse
etmeden çalıştırılabilir.

### 13.9 Sorumluluk Sınırları

Kaynak kod okuyucu aşağıdaki işlemleri yapmayacaktır:

- Klasör taramak
- Analiz kurallarını çalıştırmak
- Bulgu üretmek
- Terminal çıktısı oluşturmak
- JSON raporu oluşturmak
- Exit code belirlemek
- Syntax veya encoding hatalarını kullanıcı dostu rapora dönüştürmek

### 13.10 Kabul Kriterleri

Kaynak kod okuyucu aşağıdaki koşulları sağlamalıdır:

1. `str` ve `Path` dosya yollarını kabul eder.
2. Python dosyasını UTF-8 olarak okur.
3. Kaynak kod metnini değiştirmeden saklar.
4. Geçerli Python kodundan AST oluşturur.
5. Kaynak dosyayı yalnızca bir kez parse eder.
6. Dosya yolunu sonuç nesnesinde `Path` olarak saklar.
7. Mevcut olmayan dosya için `FileNotFoundError` üretir.
8. Dizin olarak verilen hedef için `IsADirectoryError` üretir.
9. Geçersiz Python kodu için `SyntaxError` üretir.
10. Syntax hatasında gerçek dosya yolunu gösterir.
11. UTF-8 olmayan dosya için `UnicodeDecodeError` üretir.
12. Sonucu değiştirilemez bir `SourceFile` nesnesinde tutar.

### 13.11 Test Senaryoları

`SourceReader` aşağıdaki senaryolarla doğrulanmıştır:

- Geçerli Python dosyasının okunması
- `str` dosya yolunun kabul edilmesi
- `Path` dosya yolunun kabul edilmesi
- Dosya yolunun `Path` olarak saklanması
- Kaynak kod metninin değiştirilmeden korunması
- AST yapısının oluşturulması
- Mevcut olmayan dosyanın reddedilmesi
- Dizin hedefinin reddedilmesi
- Geçersiz Python kodunda `SyntaxError` üretilmesi
- Syntax hatasında gerçek dosya yolunun bulunması
- UTF-8 olmayan dosyada `UnicodeDecodeError` üretilmesi
- Kaynak kodun yalnızca bir kez parse edilmesi
## 14. Analiz Motoru Gereksinimleri

### 14.1 Amaç

Analiz motoru, kaynak kod okuyucu tarafından oluşturulan `SourceFile`
nesnesi üzerinde kayıtlı statik analiz kurallarını çalıştırmakla sorumludur.

Her kuralın ürettiği bulgular ortak bir listede toplanarak çağıran katmana
döndürülmelidir.

Analiz motoru kaynak dosyayı tekrar okumamalı veya tekrar parse etmemelidir.
`SourceFile` içerisinde bulunan hazır AST yapısını kullanmalıdır.

### 14.2 Girdiler

Analiz motoru iki temel girdiye ihtiyaç duyar:

1. Çalıştırılacak analiz kuralları
2. Analiz edilecek `SourceFile` nesnesi

Kurallar `BaseRule` arayüzünü uygulamalıdır:

```python
Iterable[BaseRule]
```

Analiz edilecek kaynak kod aşağıdaki modelle temsil edilmelidir:

```python
SourceFile
```

### 14.3 Kural Kaydı

Analiz motorunun constructor metodu çalıştırılacak kuralları kabul etmelidir.

Örnek:

```python
engine = AnalysisEngine(
    rules=[
        LongFunctionRule(),
        LongClassRule(),
    ]
)
```

Constructor metoduna verilen kurallar motor içerisinde değiştirilemez bir
koleksiyon olarak saklanmalıdır.

Bu amaçla kuralların `tuple` yapısına dönüştürülmesi planlanmaktadır:

```python
self.rules = tuple(rules)
```

Hiç kural verilmemesi geçerli bir durumdur. Bu durumda analiz sonucunda boş
bulgu listesi döndürülmelidir.

### 14.4 Kuralların Çalıştırılması

Her kayıtlı kural analiz sırasında bir kez çalıştırılmalıdır.

Her kurala aynı AST nesnesi ve gerçek kaynak dosya yolu gönderilmelidir:

```python
rule.check(
    source_file.tree,
    str(source_file.file_path),
)
```

Kaynak kod analiz motoru içerisinde tekrar parse edilmemelidir.

### 14.5 Bulguların Toplanması

Her kural sıfır, bir veya birden fazla `Finding` nesnesi döndürebilir.

Analiz motoru bütün kuralların bulgularını tek bir listede birleştirmelidir:

```python
list[Finding]
```

Örnek:

```text
LongFunctionRule -> 2 bulgu
LongClassRule    -> 1 bulgu
Toplam           -> 3 bulgu
```

Hiçbir kural bulgu üretmezse boş liste döndürülmelidir:

```python
[]
```

### 14.6 Bulgu Sırası

İlk sürümde bulgular aşağıdaki sıraya göre korunmalıdır:

1. Kuralların analiz motoruna verildiği sıra
2. Her kuralın kendi içerisinde döndürdüğü bulgu sırası

Analiz motoru ilk sürümde bulguları ayrıca sıralamayacaktır.

Bu yaklaşım kuralların çalışma davranışını öngörülebilir ve test edilebilir
tutar.

### 14.7 Hata Davranışı

Bir analiz kuralının beklenmeyen hata üretmesi sessizce yok
sayılmamalıdır.

İlk sürümde analiz motoru kural hatalarını gizlemeyecek ve oluşan exception
çağıran katmana iletilecektir.

Bir dosyadaki veya kuraldaki hatadan sonra diğer dosyaların analizine devam
etme sorumluluğu ileride geliştirilecek üst seviye koordinasyon veya CLI
katmanında ele alınacaktır.

### 14.8 Sorumluluk Sınırları

Analiz motoru aşağıdaki işlemleri yapmayacaktır:

- Klasör taramak
- Python dosyalarını bulmak
- Kaynak dosyayı okumak
- Kaynak kodu parse etmek
- AST oluşturmak
- Terminal çıktısı oluşturmak
- JSON raporu oluşturmak
- Exit code belirlemek
- Dosya okuma hatalarını yönetmek
- Syntax hatalarını yönetmek

Bu sorumluluklar `FileScanner`, `SourceReader`, raporlama ve CLI
bileşenlerinde ele alınacaktır.

### 14.9 Kabul Kriterleri

Analiz motoru aşağıdaki koşulları sağlamalıdır:

1. `BaseRule` nesnelerinden oluşan bir iterable kabul eder.
2. Kuralları değiştirilemez bir `tuple` içerisinde saklar.
3. Boş kural listesiyle çalışabilir.
4. Analiz için bir `SourceFile` nesnesi kabul eder.
5. Her kayıtlı kuralı yalnızca bir kez çalıştırır.
6. Her kurala aynı AST nesnesini gönderir.
7. Her kurala gerçek kaynak dosya yolunu gönderir.
8. Kaynak kodu tekrar parse etmez.
9. Bir kuralın ürettiği bulguları döndürür.
10. Birden fazla kuralın bulgularını ortak listede toplar.
11. Bir kuralın birden fazla bulgusunu korur.
12. Hiç bulgu bulunmadığında boş liste döndürür.
13. Kuralların ve bulguların çalışma sırasını korur.
14. Kural exception'larını sessizce gizlemez.

### 14.10 Planlanan Test Senaryoları

Analiz motoru aşağıdaki senaryolarla doğrulanacaktır:

- Boş kural koleksiyonuyla analiz
- Kuralların `tuple` olarak saklanması
- Tek kuralın çalıştırılması
- Birden fazla kuralın çalıştırılması
- Her kuralın yalnızca bir kez çalıştırılması
- AST nesnesinin kurala doğru aktarılması
- Dosya yolunun kurala doğru aktarılması
- Tek bulgunun döndürülmesi
- Birden fazla bulgunun birleştirilmesi
- Bulgu sırasının korunması
- Hiç bulgu olmadığında boş liste döndürülmesi
- Kural exception'ının gizlenmemesi

## 15. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Teknik Tasarım](technical-design.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)