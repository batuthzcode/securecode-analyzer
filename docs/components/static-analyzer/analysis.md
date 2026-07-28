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
- `AnalysisEngine` sınıfı geliştirildi.
- Analiz kurallarının değiştirilemez bir `tuple` içerisinde saklanması sağlandı.
- Kayıtlı kuralların aynı AST nesnesi üzerinde çalıştırılması sağlandı.
- Her kurala gerçek kaynak dosya yolunun iletilmesi sağlandı.
- Birden fazla kuralın bulgularının ortak listede birleştirilmesi sağlandı.
- Kural ve bulgu sırasının korunması sağlandı.
- Analiz sırasında kaynak kodun tekrar parse edilmesi engellendi.
- Kural exception'larının gizlenmeden çağıran katmana iletilmesi sağlandı.
- Analiz motoru 12 test senaryosuyla doğrulandı.
- Python kaynak dosyalarının UTF-8 olarak okunması sağlandı.
- Kaynak kodun `ast.parse()` ile AST yapısına dönüştürülmesi sağlandı.
- AST oluşturulurken gerçek dosya yolunun kullanılması sağlandı.
- Syntax hatalarının gizlenmeden iletilmesi sağlandı.
- UTF-8 encoding hatalarının gizlenmeden iletilmesi sağlandı.
- Kaynak dosyalarının yalnızca bir kez parse edilmesi sağlandı.
- Kaynak kod okuyucu 11 test senaryosuyla doğrulandı.
- Projenin toplam 192 testi başarılı şekilde çalışmaktadır.
- `BaseTextRule` soyut kural arayüzü geliştirildi.
- Metin tabanlı kuralların kaynak kod metni ve dosya yolu alması sağlandı.
- `BaseTextRule` sınıfının public kural paketi üzerinden dışa aktarılması sağlandı.
- `AnalysisEngine` içerisine metin tabanlı kural desteği eklendi.
- AST tabanlı kurallara mevcut AST nesnesinin gönderilmesi korundu.
- Metin tabanlı kurallara `SourceFile.source` değerinin gönderilmesi sağlandı.
- AST ve metin tabanlı kuralların kayıt sırasına göre çalıştırılması sağlandı.
- Farklı kural türlerinin bulgularının ortak listede birleştirilmesi sağlandı.
- Kaynak dosyanın tekrar okunmaması ve tekrar parse edilmemesi doğrulandı.
- Metin tabanlı kural altyapısı 12 test senaryosuyla doğrulandı.
- `TodoFixmeRule` sınıfı geliştirildi.
- Python yorum tokenlarının `tokenize` ile incelenmesi sağlandı.
- Büyük-küçük harf duyarsız `TODO` ve `FIXME` tespiti eklendi.
- String literal ve bağımsız kelime olmayan ifadelerin yok sayılması sağlandı.
- Doğru satır ve sütun konumlarının bulgulara aktarılması sağlandı.
- `TodoFixmeRule` 19 test senaryosuyla doğrulandı.
- `EmptyExceptRule` sınıfı geliştirildi.
- AST içerisindeki `ExceptHandler` düğümlerinin incelenmesi sağlandı.
- Yalnızca `pass` ifadelerinden oluşan handler bloklarının tespiti eklendi.
- Bare, typed ve `except*` handler yapıları desteklendi.
- Gerçek işlem ve `raise` içeren handler bloklarının yok sayılması sağlandı.
- İç içe handler yapılarının kaynak sırasıyla raporlanması sağlandı.
- `EmptyExceptRule` 19 test senaryosuyla doğrulandı.
- `HardcodedSecretRule` sınıfı geliştirildi.
- Hassas değişken isimlerinin büyük-küçük harf duyarsız incelenmesi sağlandı.
- Normal, annotated ve attribute atamalarının desteklenmesi sağlandı.
- Birden fazla hassas atama hedefi için ayrı bulgular üretilmesi sağlandı.
- Boş string, ortam değişkeni, fonksiyon çağrısı ve string olmayan değerlerin yok sayılması sağlandı.
- Gerçek secret değerlerinin bulgu mesajında gösterilmemesi sağlandı.
- `HardcodedSecretRule` 22 test senaryosuyla doğrulandı.
- `NamingConventionRule` sınıfı geliştirildi.
- Fonksiyon ve metot isimlerinin `snake_case` biçiminde doğrulanması sağlandı.
- Sınıf isimlerinin `PascalCase` biçiminde doğrulanması sağlandı.
- Normal ve asenkron fonksiyonların kontrol edilmesi sağlandı.
- Sınıf metotlarının ve iç içe tanımların kontrol edilmesi sağlandı.
- Python dunder metotlarının isimlendirme kontrolü dışında tutulması sağlandı.
- Geçersiz fonksiyon ve sınıf isimleri için ayrı mesajlar üretilmesi sağlandı.
- İsimlendirme bulgularının `INFO` önem seviyesinde üretilmesi sağlandı.
- `NamingConventionRule` 25 test senaryosuyla doğrulandı.
- `ProjectAnalyzer` sınıfı geliştirildi.
- `FileScanner`, `SourceReader` ve `AnalysisEngine` bağımlılıklarının constructor üzerinden alınması sağlandı.
- Scanner tarafından döndürülen bütün Python dosyalarının işlenmesi sağlandı.
- Her dosyanın tam olarak bir kez okunması sağlandı.
- Her `SourceFile` nesnesinin tam olarak bir kez analiz edilmesi sağlandı.
- Farklı dosyalardan gelen bulguların birleştirilmesi sağlandı.
- Bulguların dosya yolu, satır, sütun ve kural kimliğine göre sıralanması sağlandı.
- `None` sütun numaralarının sıralama sırasında `0` olarak değerlendirilmesi sağlandı.
- Scanner, reader ve engine hatalarının değiştirilmeden iletilmesi sağlandı.
- Bulgu nesnelerinin değiştirilmeden döndürülmesi sağlandı.
- `ProjectAnalyzer` 20 test senaryosuyla doğrulandı.
- `create_default_rules()` fonksiyonu geliştirildi.
- `create_default_analyzer()` fonksiyonu geliştirildi.
- Altı varsayılan analiz kuralının `SA001` ile `SA006` arasında kararlı sırada oluşturulması sağlandı.
- Varsayılan kuralların immutable tuple olarak döndürülmesi sağlandı.
- Her factory çağrısında yeni kural nesneleri oluşturulması sağlandı.
- `LongFunctionRule` ve `LongClassRule` sınıflarının varsayılan eşiklerle oluşturulması sağlandı.
- Gerçek `FileScanner`, `SourceReader`, `AnalysisEngine` ve `ProjectAnalyzer` bileşenlerinin birbirine bağlanması sağlandı.
- Her analyzer çağrısında bağımsız bileşenler oluşturulması sağlandı.
- Factory tarafından oluşturulan analyzer geçici bir proje üzerinde uçtan uca doğrulandı.
- Var olmayan hedef hatasının değiştirilmeden iletilmesi sağlandı.
- Default analyzer factory 16 test senaryosuyla doğrulandı.

Henüz tamamlanmayan çalışmalar:

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
## 15. Metin Tabanlı Kural Arayüzü Gereksinimleri

### 15.1 Amaç

Metin tabanlı kural arayüzü, AST içerisinde doğrudan korunmayan kaynak kod
bilgilerinin analiz edilmesini sağlayacaktır.

Bu arayüz özellikle aşağıdaki kontroller için kullanılacaktır:

- `TODO` ifadelerinin tespiti
- `FIXME` ifadelerinin tespiti
- Şüpheli hardcoded secret değerlerinin aranması
- Kaynak kod içerisindeki metin desenlerinin kontrol edilmesi

AST tabanlı ve metin tabanlı kurallar ayrı sözleşmeler kullanacaktır.

### 15.2 Arayüz

Metin tabanlı kurallar aşağıdaki soyut sınıfı uygulamalıdır:

```python
class BaseTextRule(ABC):
    rule_id: str
    name: str
    description: str

    @abstractmethod
    def check(
        self,
        source: str,
        file_path: str,
    ) -> list[Finding]:
        ...
```

Her metin tabanlı kural aşağıdaki girdileri almalıdır:

- Kaynak dosyanın tam metni
- Kaynak dosyanın yolu

Kurallar tespit ettikleri problemleri `Finding` nesneleri olarak
döndürmelidir.

### 15.3 AST Kurallarından Ayrılması

Mevcut `BaseRule` arayüzü AST tabanlı kurallar için kullanılmaya devam
edecektir:

```python
def check(
    self,
    tree: ast.AST,
    file_path: str,
) -> list[Finding]:
    ...
```

Yeni `BaseTextRule` ise kaynak metne ihtiyaç duyan kurallar için
kullanılacaktır:

```python
def check(
    self,
    source: str,
    file_path: str,
) -> list[Finding]:
    ...
```

Bu ayrım sayesinde AST tabanlı kuralların mevcut sözleşmesi
değiştirilmeyecektir.

### 15.4 AnalysisEngine Entegrasyonu

`AnalysisEngine`, kayıtlı kuralın türüne göre doğru girdiyi göndermelidir.

AST tabanlı kurallar için:

```python
rule.check(
    source_file.tree,
    str(source_file.file_path),
)
```

Metin tabanlı kurallar için:

```python
rule.check(
    source_file.source,
    str(source_file.file_path),
)
```

Kaynak dosya tekrar okunmamalı ve AST tekrar oluşturulmamalıdır.

`SourceFile` içerisindeki mevcut `source` ve `tree` alanları
kullanılmalıdır.

### 15.5 Kural Sırası

AST ve metin tabanlı kurallar, `AnalysisEngine` constructor metoduna
verildikleri sırada çalıştırılmalıdır.

Örnek:

```python
engine = AnalysisEngine(
    rules=[
        LongFunctionRule(),
        TodoFixmeRule(),
        LongClassRule(),
    ]
)
```

Bu örnekte çalışma sırası aşağıdaki gibi olmalıdır:

1. `LongFunctionRule`
2. `TodoFixmeRule`
3. `LongClassRule`

Kuralların ürettiği bulguların sırası korunmalıdır.

### 15.6 Hata Davranışı

Metin tabanlı bir kuralın ürettiği beklenmeyen exception sessizce
gizlenmemelidir.

Hata, mevcut AST tabanlı kural davranışıyla tutarlı şekilde çağıran
katmana iletilmelidir.

### 15.7 Sorumluluk Sınırları

`BaseTextRule` aşağıdaki işlemleri yapmayacaktır:

- Dosya sisteminden kaynak dosya okumak
- AST oluşturmak
- Klasör taramak
- Terminal çıktısı oluşturmak
- JSON raporu oluşturmak
- Exit code belirlemek

Bu işlemler diğer bileşenlerin sorumluluğundadır.

### 15.8 Kabul Kriterleri

Metin tabanlı kural altyapısı aşağıdaki koşulları sağlamalıdır:

1. `BaseTextRule` doğrudan oluşturulamaz.
2. Somut bir metin kuralı `check()` metodunu uygulayabilir.
3. Kural kaynak kod metnini alır.
4. Kural gerçek dosya yolunu alır.
5. Kural sıfır, bir veya birden fazla `Finding` döndürebilir.
6. `AnalysisEngine` AST tabanlı kuralları desteklemeye devam eder.
7. `AnalysisEngine` metin tabanlı kuralları çalıştırabilir.
8. AST kurallarına mevcut AST nesnesi gönderilir.
9. Metin kurallarına mevcut kaynak kod metni gönderilir.
10. Kaynak dosya tekrar okunmaz.
11. Kaynak kod tekrar parse edilmez.
12. AST ve metin kurallarının çalışma sırası korunur.
13. Kural exception'ları gizlenmez.

### 15.9 Planlanan Test Senaryoları

Metin tabanlı kural altyapısı aşağıdaki senaryolarla doğrulanacaktır:

- `BaseTextRule` sınıfının doğrudan oluşturulamaması
- Somut bir metin kuralının oluşturulabilmesi
- Kaynak kod metninin kurala aktarılması
- Gerçek dosya yolunun kurala aktarılması
- AST tabanlı kural desteğinin korunması
- Metin tabanlı kuralın AnalysisEngine tarafından çalıştırılması
- AST ve metin kurallarının birlikte çalıştırılması
- Kural çalışma sırasının korunması
- Bulguların ortak listede birleştirilmesi
- Kaynak kodun tekrar okunmaması
- AST yapısının tekrar oluşturulmaması
- Metin kuralı exception'ının gizlenmemesi
## 16. TODO/FIXME Kuralı Gereksinimleri

### 16.1 Amaç

`TodoFixmeRule`, Python kaynak kodundaki yorum satırlarında bulunan `TODO` ve
`FIXME` ifadelerini tespit edecektir.

Kural, tamamlanmamış geliştirme işleri ve düzeltilmesi gereken kod bölümlerinin
görünür hâle getirilmesini amaçlamaktadır.

Kural kimliği:

```text
SA003
```

### 16.2 Kural Türü

`TodoFixmeRule`, kaynak kod yorumlarına ihtiyaç duyduğu için
`BaseTextRule` arayüzünü uygulayacaktır.

Kural sözleşmesi:

```python
def check(
    self,
    source: str,
    file_path: str,
) -> list[Finding]:
    ...
```

Kural dosya sisteminden kaynak dosya okumayacak ve kendisine verilen kaynak
metni kullanacaktır.

### 16.3 Tokenize Kullanımı

Python AST yapısı yorum satırlarını korumadığı için bu kural AST üzerinden
çalışmayacaktır.

Kaynak kodun tamamında doğrudan regex taraması yapmak aşağıdaki gibi string
değerlerinin yanlış bulgu üretmesine neden olabilir:

```python
message = "TODO: this is only text"
```

Bu nedenle yorum satırlarını ayırmak için Python standart kütüphanesindeki
`tokenize` modülü kullanılacaktır.

Yalnızca `COMMENT` token türleri analiz edilecektir.

### 16.4 Desteklenen İfadeler

Kural aşağıdaki ifadeleri büyük-küçük harf duyarsız şekilde tespit etmelidir:

```text
TODO
FIXME
```

Geçerli örnekler:

```python
# TODO: add input validation
# todo improve this function
# FIXME: handle the error
# fixme remove temporary behavior
```

Aşağıdaki değerler bulgu üretmemelidir:

```python
message = "TODO: this is not a comment"
variable_todo = "value"
# TODOLIST
# PREFIXFIXME
```

İfadelerin bağımsız kelime olması gerekmektedir.

### 16.5 Bulgu Üretimi

Her tespit edilen ifade için ayrı bir `Finding` oluşturulmalıdır.

`TODO` bulgusu:

```text
rule_id: SA003
message: TODO comment found.
severity: INFO
```

`FIXME` bulgusu:

```text
rule_id: SA003
message: FIXME comment found.
severity: WARNING
```

Bulgu aşağıdaki bilgileri içermelidir:

- `SA003` kural kimliği
- Gerçek kaynak dosya yolu
- İfadenin bulunduğu satır numarası
- İfadenin başladığı sütun numarası
- İfadeye uygun mesaj
- İfadeye uygun önem seviyesi

Satır ve sütun numaraları kullanıcıya gösterilecek şekilde 1 tabanlı
olmalıdır.

### 16.6 Birden Fazla İfade

Aynı dosyada birden fazla `TODO` veya `FIXME` bulunabilir.

Her ifade ayrı bulgu üretmelidir:

```python
# TODO: add validation
# FIXME: handle invalid data
```

Aynı yorum satırında birden fazla ifade varsa soldan sağa doğru ayrı bulgular
üretilmelidir:

```python
# TODO: review this, FIXME: remove fallback
```

Bulgular kaynak kod içerisindeki doğal sıralarını korumalıdır.

### 16.7 Boş ve Temiz Kaynak Kod

Aşağıdaki durumlarda boş bulgu listesi döndürülmelidir:

- Kaynak kodun boş olması
- Kaynak kodda yorum bulunmaması
- Yorumlarda `TODO` veya `FIXME` bulunmaması
- İfadelerin yalnızca string literal içerisinde bulunması
- İfadelerin bağımsız kelime olmaması

### 16.8 Hata Davranışı

Token oluşturma sırasında meydana gelen beklenmeyen hatalar sessizce
gizlenmemelidir.

Hata, diğer kural davranışlarıyla tutarlı şekilde çağıran katmana
iletilmelidir.

### 16.9 Sorumluluk Sınırları

`TodoFixmeRule` aşağıdaki işlemleri yapmayacaktır:

- Dosya veya klasör taramak
- Kaynak dosyayı dosya sisteminden okumak
- AST oluşturmak
- Terminal çıktısı hazırlamak
- JSON raporu hazırlamak
- Exit code belirlemek
- Diğer analiz kurallarını çalıştırmak

### 16.10 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamalıdır:

1. `BaseTextRule` arayüzünü uygulamalıdır.
2. Kural kimliği `SA003` olmalıdır.
3. Yalnızca Python yorum tokenları incelenmelidir.
4. `TODO` ifadeleri büyük-küçük harf duyarsız bulunmalıdır.
5. `FIXME` ifadeleri büyük-küçük harf duyarsız bulunmalıdır.
6. String literal içerisindeki ifadeler yok sayılmalıdır.
7. Bağımsız kelime olmayan ifadeler yok sayılmalıdır.
8. Her ifade için ayrı bulgu oluşturulmalıdır.
9. `TODO` bulguları `INFO` önem seviyesinde olmalıdır.
10. `FIXME` bulguları `WARNING` önem seviyesinde olmalıdır.
11. Gerçek dosya yolu bulguya aktarılmalıdır.
12. Satır ve sütun numaraları doğru hesaplanmalıdır.
13. Bulgular kaynak kod sırasını korumalıdır.
14. Kaynak dosya kural tarafından tekrar okunmamalıdır.
15. Beklenmeyen tokenization hataları gizlenmemelidir.

### 16.11 Planlanan Test Senaryoları

Kural aşağıdaki testlerle doğrulanacaktır:

- Varsayılan kural metadata değerleri
- `BaseTextRule` arayüzünün uygulanması
- Boş kaynak kod
- Yorum içermeyen kaynak kod
- Büyük harfli `TODO`
- Küçük harfli `todo`
- Büyük harfli `FIXME`
- Küçük harfli `fixme`
- Aynı dosyada birden fazla ifade
- Aynı yorumda birden fazla ifade
- String literal içerisindeki ifadenin yok sayılması
- Değişken adındaki ifadenin yok sayılması
- Bağımsız kelime olmayan ifadenin yok sayılması
- Gerçek dosya yolunun kullanılması
- Doğru satır numarasının üretilmesi
- Doğru sütun numarasının üretilmesi
- Bulguların kaynak sırasını koruması
- `TODO` önem seviyesinin `INFO` olması
- `FIXME` önem seviyesinin `WARNING` olması
## 16. TODO/FIXME Kuralı Gereksinimleri

### 16.1 Amaç

`TodoFixmeRule`, Python kaynak kodundaki yorum satırlarında bulunan `TODO` ve
`FIXME` ifadelerini tespit edecektir.

Kural, tamamlanmamış geliştirme işleri ve düzeltilmesi gereken kod bölümlerinin
görünür hâle getirilmesini amaçlamaktadır.

Kural kimliği:

```text
SA003
```

### 16.2 Kural Türü

`TodoFixmeRule`, kaynak kod yorumlarına ihtiyaç duyduğu için
`BaseTextRule` arayüzünü uygulayacaktır.

Kural sözleşmesi:

```python
def check(
    self,
    source: str,
    file_path: str,
) -> list[Finding]:
    ...
```

Kural dosya sisteminden kaynak dosya okumayacak ve kendisine verilen kaynak
metni kullanacaktır.

### 16.3 Tokenize Kullanımı

Python AST yapısı yorum satırlarını korumadığı için bu kural AST üzerinden
çalışmayacaktır.

Kaynak kodun tamamında doğrudan regex taraması yapmak aşağıdaki gibi string
değerlerinin yanlış bulgu üretmesine neden olabilir:

```python
message = "TODO: this is only text"
```

Bu nedenle yorum satırlarını ayırmak için Python standart kütüphanesindeki
`tokenize` modülü kullanılacaktır.

Yalnızca `COMMENT` token türleri analiz edilecektir.

### 16.4 Desteklenen İfadeler

Kural aşağıdaki ifadeleri büyük-küçük harf duyarsız şekilde tespit etmelidir:

```text
TODO
FIXME
```

Geçerli örnekler:

```python
# TODO: add input validation
# todo improve this function
# FIXME: handle the error
# fixme remove temporary behavior
```

Aşağıdaki değerler bulgu üretmemelidir:

```python
message = "TODO: this is not a comment"
variable_todo = "value"
# TODOLIST
# PREFIXFIXME
```

İfadelerin bağımsız kelime olması gerekmektedir.

### 16.5 Bulgu Üretimi

Her tespit edilen ifade için ayrı bir `Finding` oluşturulmalıdır.

`TODO` bulgusu:

```text
rule_id: SA003
message: TODO comment found.
severity: INFO
```

`FIXME` bulgusu:

```text
rule_id: SA003
message: FIXME comment found.
severity: WARNING
```

Bulgu aşağıdaki bilgileri içermelidir:

- `SA003` kural kimliği
- Gerçek kaynak dosya yolu
- İfadenin bulunduğu satır numarası
- İfadenin başladığı sütun numarası
- İfadeye uygun mesaj
- İfadeye uygun önem seviyesi

Satır ve sütun numaraları kullanıcıya gösterilecek şekilde 1 tabanlı
olmalıdır.

### 16.6 Birden Fazla İfade

Aynı dosyada birden fazla `TODO` veya `FIXME` bulunabilir.

Her ifade ayrı bulgu üretmelidir:

```python
# TODO: add validation
# FIXME: handle invalid data
```

Aynı yorum satırında birden fazla ifade varsa soldan sağa doğru ayrı bulgular
üretilmelidir:

```python
# TODO: review this, FIXME: remove fallback
```

Bulgular kaynak kod içerisindeki doğal sıralarını korumalıdır.

### 16.7 Boş ve Temiz Kaynak Kod

Aşağıdaki durumlarda boş bulgu listesi döndürülmelidir:

- Kaynak kodun boş olması
- Kaynak kodda yorum bulunmaması
- Yorumlarda `TODO` veya `FIXME` bulunmaması
- İfadelerin yalnızca string literal içerisinde bulunması
- İfadelerin bağımsız kelime olmaması

### 16.8 Hata Davranışı

Token oluşturma sırasında meydana gelen beklenmeyen hatalar sessizce
gizlenmemelidir.

Hata, diğer kural davranışlarıyla tutarlı şekilde çağıran katmana
iletilmelidir.

### 16.9 Sorumluluk Sınırları

`TodoFixmeRule` aşağıdaki işlemleri yapmayacaktır:

- Dosya veya klasör taramak
- Kaynak dosyayı dosya sisteminden okumak
- AST oluşturmak
- Terminal çıktısı hazırlamak
- JSON raporu hazırlamak
- Exit code belirlemek
- Diğer analiz kurallarını çalıştırmak

### 16.10 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamalıdır:

1. `BaseTextRule` arayüzünü uygulamalıdır.
2. Kural kimliği `SA003` olmalıdır.
3. Yalnızca Python yorum tokenları incelenmelidir.
4. `TODO` ifadeleri büyük-küçük harf duyarsız bulunmalıdır.
5. `FIXME` ifadeleri büyük-küçük harf duyarsız bulunmalıdır.
6. String literal içerisindeki ifadeler yok sayılmalıdır.
7. Bağımsız kelime olmayan ifadeler yok sayılmalıdır.
8. Her ifade için ayrı bulgu oluşturulmalıdır.
9. `TODO` bulguları `INFO` önem seviyesinde olmalıdır.
10. `FIXME` bulguları `WARNING` önem seviyesinde olmalıdır.
11. Gerçek dosya yolu bulguya aktarılmalıdır.
12. Satır ve sütun numaraları doğru hesaplanmalıdır.
13. Bulgular kaynak kod sırasını korumalıdır.
14. Kaynak dosya kural tarafından tekrar okunmamalıdır.
15. Beklenmeyen tokenization hataları gizlenmemelidir.

### 16.11 Planlanan Test Senaryoları

Kural aşağıdaki testlerle doğrulanacaktır:

- Varsayılan kural metadata değerleri
- `BaseTextRule` arayüzünün uygulanması
- Boş kaynak kod
- Yorum içermeyen kaynak kod
- Büyük harfli `TODO`
- Küçük harfli `todo`
- Büyük harfli `FIXME`
- Küçük harfli `fixme`
- Aynı dosyada birden fazla ifade
- Aynı yorumda birden fazla ifade
- String literal içerisindeki ifadenin yok sayılması
- Değişken adındaki ifadenin yok sayılması
- Bağımsız kelime olmayan ifadenin yok sayılması
- Gerçek dosya yolunun kullanılması
- Doğru satır numarasının üretilmesi
- Doğru sütun numarasının üretilmesi
- Bulguların kaynak sırasını koruması
- `TODO` önem seviyesinin `INFO` olması
- `FIXME` önem seviyesinin `WARNING` olması
## 17. Boş Except Kuralı Gereksinimleri

### 17.1 Amaç

`EmptyExceptRule`, Python kaynak kodunda yalnızca `pass` ifadesi içeren
`except` bloklarını tespit edecektir.

Boş exception handler blokları hataların sessizce gizlenmesine ve uygulamadaki
problemlerin fark edilmemesine neden olabilir.

Kural kimliği:

```text
SA004
```

### 17.2 Kural Türü

`EmptyExceptRule`, Python kodunun yapısal özelliklerini analiz ettiği için
`BaseRule` AST kural arayüzünü uygulayacaktır.

Kural sözleşmesi:

```python
def check(
    self,
    tree: ast.AST,
    file_path: str,
) -> list[Finding]:
    ...
```

Kural kaynak kodu tekrar parse etmeyecek ve kendisine verilen mevcut AST
nesnesini kullanacaktır.

### 17.3 Tespit Edilecek Yapılar

Aşağıdaki handler boş kabul edilmelidir:

```python
try:
    risky_operation()
except Exception:
    pass
```

Bare except kullanımı da aynı şekilde tespit edilmelidir:

```python
try:
    risky_operation()
except:
    pass
```

Bir handler içerisinde yalnızca bir veya birden fazla `pass` ifadesi
bulunuyorsa handler boş kabul edilmelidir:

```python
try:
    risky_operation()
except Exception:
    pass
    pass
```

### 17.4 Bulgu Üretmemesi Gereken Yapılar

Aşağıdaki handler blokları boş kabul edilmemelidir:

```python
try:
    risky_operation()
except Exception as error:
    logger.exception(error)
```

```python
try:
    risky_operation()
except Exception:
    raise
```

```python
try:
    risky_operation()
except Exception:
    recover()
    pass
```

Bir handler içerisinde `pass` dışında en az bir gerçek işlem varsa bulgu
oluşturulmamalıdır.

### 17.5 Bulgu Bilgileri

Her boş exception handler için bir `Finding` oluşturulmalıdır.

Bulgu özellikleri:

```text
rule_id: SA004
message: Empty except block found.
severity: WARNING
```

Bulgu aşağıdaki bilgileri içermelidir:

- `SA004` kural kimliği
- Gerçek kaynak dosya yolu
- `except` ifadesinin bulunduğu satır numarası
- Uygun sütun numarası
- Açıklayıcı mesaj
- `WARNING` önem seviyesi

AST içerisindeki satır ve sütun bilgileri kullanılmalıdır.

Kullanıcıya gösterilen sütun numarası bir tabanlı olmalıdır.

### 17.6 Birden Fazla Handler

Aynı kaynak dosyada birden fazla boş exception handler bulunabilir.

Her boş handler için ayrı bir bulgu oluşturulmalıdır:

```python
try:
    first_operation()
except ValueError:
    pass

try:
    second_operation()
except RuntimeError:
    pass
```

Bulgular kaynak kod içerisindeki doğal sıralarını korumalıdır.

### 17.7 İç İçe Yapılar

İç içe fonksiyon, sınıf veya exception bloklarında bulunan boş handler
yapıları ayrı ayrı tespit edilmelidir.

Örnek:

```python
def process() -> None:
    try:
        first_operation()
    except ValueError:
        pass

    class Handler:
        def run(self) -> None:
            try:
                second_operation()
            except RuntimeError:
                pass
```

Bu kaynak kod iki ayrı bulgu üretmelidir.

### 17.8 Try-Star Desteği

Python `except*` yapıları AST içerisinde `ExceptHandler` düğümleriyle temsil
edildiğinde aynı boş handler kontrolü uygulanmalıdır.

Örnek:

```python
try:
    raise ExceptionGroup("errors", [ValueError()])
except* ValueError:
    pass
```

### 17.9 Hata Davranışı

Kural kendisine verilen AST nesnesini değiştirmemelidir.

Analiz sırasında meydana gelen beklenmeyen exception'lar sessizce
gizlenmemeli ve çağıran katmana iletilmelidir.

### 17.10 Sorumluluk Sınırları

`EmptyExceptRule` aşağıdaki işlemleri yapmayacaktır:

- Dosya veya klasör taramak
- Kaynak dosyayı okumak
- Kaynak kodu parse etmek
- Terminal çıktısı hazırlamak
- JSON raporu hazırlamak
- Exit code belirlemek
- Diğer analiz kurallarını çalıştırmak

### 17.11 Kabul Kriterleri

Kural aşağıdaki koşulları sağlamalıdır:

1. `BaseRule` arayüzünü uygulamalıdır.
2. Kural kimliği `SA004` olmalıdır.
3. Yalnızca `pass` içeren exception handler bloklarını tespit etmelidir.
4. Bare except bloklarını desteklemelidir.
5. Belirli exception türlerini yakalayan handler bloklarını desteklemelidir.
6. Birden fazla `pass` içeren handler bloklarını boş kabul etmelidir.
7. Gerçek işlem içeren handler bloklarını yok saymalıdır.
8. `raise` içeren handler bloklarını yok saymalıdır.
9. Her boş handler için ayrı bulgu oluşturmalıdır.
10. İç içe handler bloklarını tespit etmelidir.
11. Bulgular kaynak kod sırasını korumalıdır.
12. Gerçek dosya yolunu bulguya aktarmalıdır.
13. Doğru satır ve sütun konumunu üretmelidir.
14. Bulgular `WARNING` önem seviyesinde olmalıdır.
15. Mevcut AST nesnesini kullanmalı ve kaynak kodu tekrar parse etmemelidir.

### 17.12 Planlanan Test Senaryoları

Kural aşağıdaki testlerle doğrulanacaktır:

- Varsayılan metadata değerleri
- `BaseRule` arayüzünün uygulanması
- Boş AST kaynağında bulgu oluşmaması
- Yalnızca `pass` içeren typed except
- Yalnızca `pass` içeren bare except
- Birden fazla `pass` içeren handler
- Loglama işlemi içeren handler
- Yeniden exception fırlatan handler
- Gerçek işlem ve `pass` içeren handler
- Birden fazla boş handler
- İç içe boş handler
- Gerçek dosya yolunun kullanılması
- Doğru satır numarası
- Bir tabanlı sütun numarası
- `SA004` kural kimliği
- Doğru mesaj
- `WARNING` önem seviyesi
- Bulguların kaynak sırasını koruması
- Mevcut AST nesnesinin değiştirilmemesi
## 18. Hardcoded Secret Kuralı Gereksinimleri

### 18.1 Amaç

`HardcodedSecretRule`, hassas bilgi ifade eden değişkenlere doğrudan atanmış
string literal değerlerini tespit edecektir.

Kural kimliği:

```text
SA005
```

Bu kural kesin bir güvenlik açığı doğrulaması değil, inceleme gerektiren
şüpheli bir bulgu üretir.

### 18.2 Kural Türü

Kural, değişken adı ile atanan değerin yapısal ilişkisini inceleyeceği için
`BaseRule` AST arayüzünü uygulayacaktır:

```python
def check(
    self,
    tree: ast.AST,
    file_path: str,
) -> list[Finding]:
    ...
```

Kural kaynak dosyayı okumayacak ve kaynak kodu tekrar parse etmeyecektir.

### 18.3 Hassas Değişken Adları

İlk sürümde aşağıdaki isimler ve bunları içeren snake_case değişken adları
şüpheli kabul edilmelidir:

```text
password
passwd
pwd
secret
token
api_key
apikey
access_token
auth_token
client_secret
private_key
```

Bulgu üretmesi gereken örnekler:

```python
password = "admin123"
database_password = "secret-value"
api_key = "abc123"
github_token = "token-value"
client_secret: str = "client-secret-value"
```

Değişken adı kontrolü büyük-küçük harf duyarsız olmalıdır.

### 18.4 Desteklenen Atamalar

Kural aşağıdaki AST atamalarını desteklemelidir:

```python
password = "admin123"
```

```python
api_key: str = "abc123"
```

Attribute atamaları da desteklenmelidir:

```python
config.password = "admin123"
```

Birden fazla hedefe yapılan atamalarda bütün hassas hedefler
değerlendirilmelidir:

```python
password = backup_password = "admin123"
```

### 18.5 Bulgu Üretmemesi Gereken Değerler

Yalnızca doğrudan yazılmış, boş olmayan string literal değerleri
raporlanmalıdır.

Aşağıdaki örnekler bulgu üretmemelidir:

```python
password = ""
token = "   "
api_key = os.getenv("API_KEY")
secret = load_secret()
password = None
token = 12345
```

Değişken adında hassas ifade bulunmuyorsa string değer bulgu üretmemelidir:

```python
username = "admin"
message = "secret"
```

String içerisinde hassas kelime bulunması tek başına yeterli değildir.

### 18.6 Bulgu Bilgileri

Her şüpheli atama için bir `Finding` oluşturulmalıdır:

```text
rule_id: SA005
message: Possible hardcoded secret found.
severity: WARNING
```

Bulgu aşağıdaki bilgileri içermelidir:

- `SA005` kural kimliği
- Gerçek dosya yolu
- Hassas değişkenin satır numarası
- Bir tabanlı sütun numarası
- Açıklayıcı mesaj
- `WARNING` önem seviyesi

Bulgu mesajına gerçek secret değeri eklenmemelidir.

### 18.7 Sıralama ve Tekrarlanan Bulgular

Bir dosyada birden fazla hardcoded secret bulunabilir.

Her hassas hedef için ayrı bulgu oluşturulmalıdır ve bulgular kaynak kod
sırasını korumalıdır.

```python
password = "first"
api_key = "second"
client_secret = "third"
```

Aynı AST hedefi için tekrar eden bulgu üretilmemelidir.

### 18.8 Hata ve Sorumluluk Sınırları

Kural:

- Kaynak dosyayı okumamalıdır.
- Kaynak kodu tekrar parse etmemelidir.
- Verilen AST nesnesini değiştirmemelidir.
- Secret değerlerini terminale veya bulgu mesajına yazmamalıdır.
- Terminal veya JSON raporu üretmemelidir.
- Exit code belirlememelidir.
- Beklenmeyen exception'ları gizlememelidir.

### 18.9 Kabul Kriterleri

1. `BaseRule` arayüzünü uygulamalıdır.
2. Kural kimliği `SA005` olmalıdır.
3. Hassas değişken adlarını büyük-küçük harf duyarsız tespit etmelidir.
4. Normal atamaları desteklemelidir.
5. Type annotation içeren atamaları desteklemelidir.
6. Attribute atamalarını desteklemelidir.
7. Birden fazla atama hedefini desteklemelidir.
8. Yalnızca boş olmayan string literal değerlerini raporlamalıdır.
9. `os.getenv()` ve fonksiyon çağrılarını yok saymalıdır.
10. Hassas olmayan değişkenleri yok saymalıdır.
11. Gerçek secret değerini bulgu mesajına eklememelidir.
12. Gerçek dosya yolunu bulguya aktarmalıdır.
13. Doğru satır ve sütun konumunu üretmelidir.
14. Bulgular `WARNING` önem seviyesinde olmalıdır.
15. Bulgular kaynak kod sırasını korumalıdır.
16. Verilen AST nesnesini değiştirmemelidir.

### 18.10 Planlanan Test Senaryoları

- Varsayılan metadata değerleri
- `BaseRule` arayüzünün uygulanması
- Boş kaynak kod
- Normal password ataması
- API key ataması
- Büyük-küçük harf duyarsız değişken adı
- Snake case içerisinde hassas ifade
- Type annotation içeren atama
- Attribute ataması
- Birden fazla atama hedefi
- Boş string değerinin yok sayılması
- Yalnızca boşluk içeren değerin yok sayılması
- `os.getenv()` kullanımının yok sayılması
- Fonksiyon çağrısının yok sayılması
- Sayısal ve `None` değerlerinin yok sayılması
- Hassas olmayan değişken adının yok sayılması
- Gerçek dosya yolunun aktarılması
- Satır ve sütun konumu
- Beklenen mesaj ve önem seviyesi
- Bulguların kaynak sırası
- Secret değerinin mesajda bulunmaması
- AST nesnesinin değiştirilmemesi
## 19. İsimlendirme Kuralı Gereksinimleri

### 19.1 Amaç

`NamingConventionRule`, Python kaynak kodundaki fonksiyon, metot ve sınıf
adlarının belirlenen isimlendirme kurallarına uygunluğunu kontrol edecektir.

Kural kimliği:

```text
SA006
```

İlk sürümde aşağıdaki kurallar uygulanacaktır:

- Fonksiyon ve metot adları `snake_case` olmalıdır.
- Sınıf adları `PascalCase` olmalıdır.

### 19.2 Kural Türü

Kural, fonksiyon ve sınıf tanımlarını yapısal olarak inceleyeceği için
`BaseRule` AST arayüzünü uygulayacaktır:

```python
def check(
    self,
    tree: ast.AST,
    file_path: str,
) -> list[Finding]:
    ...
```

Kural kaynak dosyayı okumayacak ve kaynak kodu tekrar parse etmeyecektir.

### 19.3 Fonksiyon İsimlendirmesi

Normal ve asenkron fonksiyon adları `snake_case` biçiminde olmalıdır.

Geçerli örnekler:

```python
def calculate_total() -> int:
    return 0


async def fetch_user_data() -> None:
    pass


def _internal_helper() -> None:
    pass
```

Geçersiz örnekler:

```python
def CalculateTotal() -> int:
    return 0


def calculateTotal() -> int:
    return 0


async def FetchUserData() -> None:
    pass
```

Fonksiyon adları:

- Küçük harfle başlamalıdır.
- Küçük harf, rakam ve alt çizgi içerebilir.
- Gizli yardımcı fonksiyonlar için bir veya daha fazla başlangıç alt çizgisi
  kullanılabilir.

### 19.4 Özel Metotlar

Aşağıdaki gibi çift alt çizgiyle başlayıp biten özel metotlar kontrol dışında
tutulmalıdır:

```python
def __init__(self) -> None:
    pass


def __str__(self) -> str:
    return "Example"
```

Bu metotlar isimlendirme bulgusu üretmemelidir.

### 19.5 Sınıf İsimlendirmesi

Sınıf adları `PascalCase` biçiminde olmalıdır.

Geçerli örnekler:

```python
class UserService:
    pass


class HTTPClient:
    pass


class _InternalHandler:
    pass
```

Geçersiz örnekler:

```python
class user_service:
    pass


class userService:
    pass


class userhandler:
    pass
```

Sınıf adları:

- İsteğe bağlı başlangıç alt çizgilerinden sonra büyük harfle başlamalıdır.
- Harf ve rakam içerebilir.
- Kelimeler arasında alt çizgi kullanılmamalıdır.

### 19.6 İç İçe Yapılar

Kural aşağıdaki yapıların tamamını kontrol etmelidir:

- Modül seviyesindeki fonksiyonlar
- Sınıf metotları
- İç içe fonksiyonlar
- İç içe sınıflar
- Asenkron fonksiyonlar ve metotlar

Her uygunsuz tanım ayrı bulgu üretmelidir.

### 19.7 Bulgu Bilgileri

Geçersiz fonksiyon veya metot adı için:

```text
rule_id: SA006
message: Function name should use snake_case.
severity: INFO
```

Geçersiz sınıf adı için:

```text
rule_id: SA006
message: Class name should use PascalCase.
severity: INFO
```

Her bulgu aşağıdaki bilgileri içermelidir:

- `SA006` kural kimliği
- Gerçek kaynak dosya yolu
- Tanımın bulunduğu satır numarası
- Bir tabanlı bildirim sütunu
- Uygun mesaj
- `INFO` önem seviyesi

### 19.8 Sıralama

Bir dosyada birden fazla isimlendirme problemi bulunabilir.

Bulgular kaynak kod içerisindeki doğal sıralarını korumalıdır:

```python
def BadFunction():
    pass


class bad_class:
    pass
```

Bu örnekte fonksiyon bulgusu sınıf bulgusundan önce dönmelidir.

### 19.9 Kapsam Dışındaki İsimler

İlk sürümde aşağıdaki isimler kontrol edilmeyecektir:

- Değişken adları
- Parametre adları
- Modül adları
- Paket adları
- Sabit isimleri
- Import alias isimleri

Bunlar ileride ayrı kurallarla ele alınabilir.

### 19.10 Hata ve Sorumluluk Sınırları

Kural:

- Kaynak dosyayı okumamalıdır.
- Kaynak kodu tekrar parse etmemelidir.
- Verilen AST nesnesini değiştirmemelidir.
- Terminal veya JSON çıktısı oluşturmamalıdır.
- Exit code belirlememelidir.
- Beklenmeyen exception'ları gizlememelidir.

### 19.11 Kabul Kriterleri

1. `BaseRule` arayüzünü uygulamalıdır.
2. Kural kimliği `SA006` olmalıdır.
3. Normal fonksiyonları kontrol etmelidir.
4. Asenkron fonksiyonları kontrol etmelidir.
5. Sınıf metotlarını kontrol etmelidir.
6. İç içe fonksiyon ve sınıfları kontrol etmelidir.
7. Geçerli `snake_case` fonksiyon adlarını kabul etmelidir.
8. Geçersiz fonksiyon adlarını raporlamalıdır.
9. Dunder metotları yok saymalıdır.
10. Geçerli `PascalCase` sınıf adlarını kabul etmelidir.
11. Geçersiz sınıf adlarını raporlamalıdır.
12. Her uygunsuz tanım için ayrı bulgu üretmelidir.
13. Bulgular kaynak kod sırasını korumalıdır.
14. Gerçek dosya yolunu bulguya aktarmalıdır.
15. Doğru satır ve sütun konumunu üretmelidir.
16. Bulgular `INFO` önem seviyesinde olmalıdır.
17. Verilen AST nesnesini değiştirmemelidir.

### 19.12 Planlanan Test Senaryoları

- Varsayılan metadata değerleri
- `BaseRule` arayüzünün uygulanması
- Boş kaynak kod
- Geçerli snake case fonksiyon
- Başlangıç alt çizgili fonksiyon
- Geçersiz PascalCase fonksiyon
- Geçersiz camelCase fonksiyon
- Geçerli asenkron fonksiyon
- Geçersiz asenkron fonksiyon
- Dunder metodun yok sayılması
- Geçerli PascalCase sınıf
- Başlangıç alt çizgili sınıf
- Geçersiz snake case sınıf
- Geçersiz camelCase sınıf
- Sınıf metodunun kontrol edilmesi
- İç içe fonksiyonların kontrol edilmesi
- İç içe sınıfların kontrol edilmesi
- Birden fazla bulgu
- Gerçek dosya yolu
- Satır ve sütun konumu
- Fonksiyon bulgu mesajı
- Sınıf bulgu mesajı
- `INFO` önem seviyesi
- Kaynak sırası
- AST nesnesinin değiştirilmemesi
## 20. Project Analyzer Gereksinimleri

### 20.1 Amaç

`ProjectAnalyzer`, hedef klasörde bulunan Python kaynak dosyalarının analiz
edilmesini yöneten üst seviye koordinasyon bileşeni olacaktır.

Bu bileşen aşağıdaki mevcut sınıfları bir araya getirecektir:

- `FileScanner`
- `SourceReader`
- `AnalysisEngine`

Temel işlem sırası:

1. Hedef klasördeki Python dosyalarını keşfetmek
2. Her dosyayı okumak ve AST nesnesine dönüştürmek
3. Kayıtlı analiz kurallarını çalıştırmak
4. Bütün bulguları tek listede birleştirmek
5. Bulguları kararlı bir sırada döndürmek

### 20.2 Genel Arayüz

Sınıf aşağıdaki temel arayüzü sağlamalıdır:

```python
class ProjectAnalyzer:
    def analyze(
        self,
        target: str | Path,
    ) -> list[Finding]:
        ...
```

`target`, analiz edilecek klasörün yolu olacaktır.

Metot yalnızca bulgu listesini döndürecektir. Terminal çıktısı, JSON çıktısı
ve process exit code işlemleri bu sınıfın sorumluluğunda olmayacaktır.

### 20.3 Bağımlılıklar

`ProjectAnalyzer` aşağıdaki bağımlılıkları constructor üzerinden almalıdır:

```python
def __init__(
    self,
    scanner: FileScanner,
    reader: SourceReader,
    engine: AnalysisEngine,
) -> None:
    ...
```

Bu yaklaşım:

- Bileşenlerin birbirinden bağımsız test edilmesini
- Testlerde sahte veya izleme amaçlı bağımlılıklar kullanılmasını
- Farklı analiz motorlarının kullanılabilmesini
- Varsayılan kural seçiminin bu sınıftan ayrılmasını

sağlayacaktır.

`ProjectAnalyzer` kendi içinde analiz kuralları oluşturmamalıdır. Hangi
kuralların çalıştırılacağı `AnalysisEngine` tarafından belirlenmelidir.

### 20.4 Dosya Keşfi

Hedef klasör ilk olarak `FileScanner.scan()` metoduna verilmelidir:

```python
python_files = scanner.scan(target)
```

`ProjectAnalyzer`:

- Klasörü kendisi dolaşmamalıdır.
- `os.walk()` çağırmamalıdır.
- Hariç tutulan klasörleri tekrar değerlendirmemelidir.
- Dosya uzantılarını tekrar filtrelememelidir.

Dosya keşfiyle ilgili bütün sorumluluk `FileScanner` sınıfında kalmalıdır.

### 20.5 Kaynak Dosyaların Okunması

Scanner tarafından döndürülen her dosya tam olarak bir kez
`SourceReader.read()` metoduna verilmelidir:

```python
source_file = reader.read(file_path)
```

`ProjectAnalyzer`:

- Dosyayı doğrudan açmamalıdır.
- Kaynak kodu kendisi okumamalıdır.
- `ast.parse()` çağırmamalıdır.
- Aynı dosyayı birden fazla kez okumamalıdır.

### 20.6 Analiz Motorunun Çalıştırılması

Her `SourceFile` nesnesi tam olarak bir kez `AnalysisEngine.analyze()` metoduna
verilmelidir:

```python
file_findings = engine.analyze(source_file)
```

Her dosyadan dönen bulgular proje bulgu listesine eklenmelidir.

Bir dosya için hiç bulgu bulunmaması diğer dosyaların analiz edilmesini
engellememelidir.

### 20.7 Boş Klasör Davranışı

Hedef klasörde Python dosyası bulunmadığında:

```python
[]
```

döndürülmelidir.

Bu durumda:

- `SourceReader.read()` çağrılmamalıdır.
- `AnalysisEngine.analyze()` çağrılmamalıdır.
- Hata üretilmemelidir.

### 20.8 Bulgu Sıralaması

Sonuçlar kararlı ve öngörülebilir bir sırada döndürülmelidir.

Sıralama ölçütleri:

1. Dosya yolu
2. Satır numarası
3. Sütun numarası
4. Kural kimliği

Sütun numarası `None` olan bulgular sıralama sırasında `0` değerine sahipmiş
gibi değerlendirilmelidir.

Örnek sıralama anahtarı:

```python
(
    finding.file_path.casefold(),
    finding.line_number,
    finding.column_number or 0,
    finding.rule_id,
)
```

Bu sayede analiz motorundaki kural kayıt sırası sonuçların doğal dosya ve
satır sırasını bozmamalıdır.

### 20.9 Hata Davranışı

Alt bileşenlerden gelen hatalar gizlenmemelidir.

Örnekler:

- Var olmayan hedef için `FileNotFoundError`
- Dosya olmayan hedef için `NotADirectoryError`
- Geçersiz Python kaynak kodu için `SyntaxError`
- Geçersiz UTF-8 içeriği için `UnicodeDecodeError`

`ProjectAnalyzer` bu hataları yakalayıp boş bulgu listesine çevirmemelidir.

Beklenmeyen exception'lar da sessizce yok sayılmamalıdır.

### 20.10 Sorumluluk Sınırları

`ProjectAnalyzer` aşağıdaki işlemleri yapmamalıdır:

- Terminale çıktı yazmak
- JSON oluşturmak
- Process exit code belirlemek
- Dosya içeriğini değiştirmek
- AST nesnelerini değiştirmek
- Analiz kurallarını kendi içinde oluşturmak
- Exception'ları sessizce gizlemek
- Güvenlik açığı taraması yapmak
- Dependency veya CVE analizi yapmak

Bu işlemler sonraki katmanlarda ele alınacaktır.

### 20.11 Kabul Kriterleri

1. Hedef yol olarak `str` kabul etmelidir.
2. Hedef yol olarak `Path` kabul etmelidir.
3. `FileScanner` bağımlılığını constructor üzerinden almalıdır.
4. `SourceReader` bağımlılığını constructor üzerinden almalıdır.
5. `AnalysisEngine` bağımlılığını constructor üzerinden almalıdır.
6. Scanner tarafından döndürülen her dosyayı işlemelidir.
7. Her dosyayı tam olarak bir kez okumalıdır.
8. Her `SourceFile` nesnesini tam olarak bir kez analiz etmelidir.
9. Bütün dosyaların bulgularını birleştirmelidir.
10. Python dosyası olmayan klasör için boş liste döndürmelidir.
11. Bulguları kararlı biçimde sıralamalıdır.
12. `None` sütun numaralarını sıralayabilmelidir.
13. Aynı konumdaki bulguları kural kimliğine göre sıralamalıdır.
14. Scanner hatalarını değiştirmeden iletmelidir.
15. Reader hatalarını değiştirmeden iletmelidir.
16. Engine hatalarını değiştirmeden iletmelidir.
17. Terminal çıktısı üretmemelidir.
18. Kendisine verilen bulguları değiştirmemelidir.

### 20.12 Planlanan Test Senaryoları

- Constructor bağımlılıklarının saklanması
- String hedef yolunun kabul edilmesi
- `Path` hedef yolunun kabul edilmesi
- Boş klasör için boş liste
- Tek Python dosyasının analiz edilmesi
- Birden fazla Python dosyasının analiz edilmesi
- Her dosyanın bir kez okunması
- Her kaynak dosyanın bir kez analiz edilmesi
- Farklı dosyalardaki bulguların birleştirilmesi
- Dosya yoluna göre sıralama
- Satır numarasına göre sıralama
- Sütun numarasına göre sıralama
- `None` sütun numarasının desteklenmesi
- Aynı konumdaki bulguların kural kimliğine göre sıralanması
- Scanner `FileNotFoundError` hatasının iletilmesi
- Scanner `NotADirectoryError` hatasının iletilmesi
- Reader `SyntaxError` hatasının iletilmesi
- Reader `UnicodeDecodeError` hatasının iletilmesi
- Engine hatasının iletilmesi
- Bulgu nesnelerinin değiştirilmemesi
## 21. Default Analyzer Factory Gereksinimleri

### 21.1 Amaç

Default analyzer factory, statik analiz sisteminin varsayılan bileşenlerini
tek bir noktada oluşturacaktır.

Factory aşağıdaki bileşenlerin kurulmasını sağlayacaktır:

- Varsayılan analiz kuralları
- `FileScanner`
- `SourceReader`
- `AnalysisEngine`
- `ProjectAnalyzer`

Bu sayede CLI ve diğer istemci katmanları bütün bağımlılıkları manuel olarak
oluşturmak zorunda kalmayacaktır.

### 21.2 Genel Arayüz

Factory modülü aşağıdaki fonksiyonları sağlamalıdır:

```python
def create_default_rules() -> tuple[AnalysisRule, ...]:
    ...


def create_default_analyzer() -> ProjectAnalyzer:
    ...
```

`create_default_rules()`, varsayılan analiz kurallarını kararlı bir sırada
döndürmelidir.

`create_default_analyzer()`, bütün varsayılan bileşenleri birbirine bağlanmış
bir `ProjectAnalyzer` nesnesi döndürmelidir.

### 21.3 Varsayılan Kurallar

Factory aşağıdaki kuralları oluşturmalıdır:

1. `LongFunctionRule`
2. `LongClassRule`
3. `TodoFixmeRule`
4. `EmptyExceptRule`
5. `HardcodedSecretRule`
6. `NamingConventionRule`

Kural kimlikleri aşağıdaki sırada olmalıdır:

```text
SA001
SA002
SA003
SA004
SA005
SA006
```

Bu sıra kararlı olmalı ve testlerle doğrulanmalıdır.

### 21.4 Kural Nesnelerinin Yaşam Döngüsü

Her `create_default_rules()` çağrısı yeni kural nesneleri üretmelidir.

Örnek:

```python
first_rules = create_default_rules()
second_rules = create_default_rules()

assert first_rules is not second_rules
assert first_rules[0] is not second_rules[0]
```

Factory global ve değiştirilebilir bir kural listesi paylaşmamalıdır.

Bir istemcinin döndürülen koleksiyonu veya kural nesnelerini kullanması,
sonraki factory çağrılarını etkilememelidir.

### 21.5 Kural Koleksiyonu

Varsayılan kurallar immutable bir tuple içerisinde döndürülmelidir:

```python
(
    LongFunctionRule(),
    LongClassRule(),
    TodoFixmeRule(),
    EmptyExceptRule(),
    HardcodedSecretRule(),
    NamingConventionRule(),
)
```

Liste yerine tuple kullanılması, varsayılan kural sırasının istemci
tarafından yanlışlıkla değiştirilmesini zorlaştıracaktır.

### 21.6 Varsayılan Eşikler

`LongFunctionRule` ve `LongClassRule` kendi varsayılan eşik değerleriyle
oluşturulmalıdır.

Factory bu sürümde özel threshold parametreleri almamalıdır.

Özel eşik değerleri kullanmak isteyen istemciler kendi `AnalysisEngine`
nesnelerini oluşturabilmelidir.

### 21.7 ProjectAnalyzer Oluşturulması

`create_default_analyzer()` aşağıdaki nesneleri oluşturmalıdır:

```python
scanner = FileScanner()
reader = SourceReader()
rules = create_default_rules()
engine = AnalysisEngine(rules=rules)

return ProjectAnalyzer(
    scanner=scanner,
    reader=reader,
    engine=engine,
)
```

Döndürülen `ProjectAnalyzer` aşağıdaki gerçek bileşenleri içermelidir:

- `FileScanner`
- `SourceReader`
- `AnalysisEngine`

Engine içerisinde altı varsayılan analiz kuralı bulunmalıdır.

### 21.8 Bağımsız Analyzer Nesneleri

Her `create_default_analyzer()` çağrısı bağımsız nesneler üretmelidir.

İki ayrı çağrının aşağıdaki nesneleri paylaşmaması gerekir:

- `ProjectAnalyzer`
- `FileScanner`
- `SourceReader`
- `AnalysisEngine`
- Analiz kuralı nesneleri

Bu davranış, farklı analiz işlemlerinin birbirini etkilemesini önleyecektir.

### 21.9 Uçtan Uca Davranış

Factory tarafından oluşturulan analyzer, gerçek bir klasörü analiz
edebilmelidir.

Örneğin geçici bir Python dosyası:

```python
password = "admin123"

def BadFunction():
    pass
```

analiz edildiğinde en az aşağıdaki kural kimliklerini üretmelidir:

```text
SA005
SA006
```

Bu test factory, scanner, reader, engine, project analyzer ve kuralların
birlikte çalıştığını doğrulayacaktır.

Uçtan uca test yalnızca küçük ve geçici bir proje üzerinde çalışmalıdır.

### 21.10 Hata Davranışı

Factory tarafından oluşturulan analyzer, alt bileşenlerin hata davranışını
değiştirmemelidir.

Örneğin var olmayan bir hedef analiz edildiğinde `FileNotFoundError`
çağıran katmana iletilmelidir.

Factory:

- Exception yakalamamalıdır.
- Hataları boş bulgu listesine çevirmemelidir.
- Terminale hata mesajı yazmamalıdır.

### 21.11 Sorumluluk Sınırları

Default analyzer factory aşağıdaki işlemleri yapmamalıdır:

- Hedef klasörü analiz etmek
- Dosya okumak
- AST oluşturmak
- Terminal çıktısı üretmek
- JSON çıktısı üretmek
- Process exit code belirlemek
- CLI argümanlarını parse etmek
- Dependency veya CVE taraması yapmak
- Global değiştirilebilir kural listesi saklamak
- Kullanıcı yapılandırması okumak

Factory yalnızca nesneleri oluşturmak ve birbirine bağlamakla sorumludur.

### 21.12 Kabul Kriterleri

1. `create_default_rules()` fonksiyonu bulunmalıdır.
2. `create_default_analyzer()` fonksiyonu bulunmalıdır.
3. Varsayılan kurallar tuple olarak döndürülmelidir.
4. Tam olarak altı varsayılan kural bulunmalıdır.
5. Kural kimlikleri `SA001` ile `SA006` arasında sıralanmalıdır.
6. Bütün varsayılan kural sınıfları kullanılmalıdır.
7. Her çağrı yeni kural nesneleri üretmelidir.
8. `LongFunctionRule` varsayılan threshold ile oluşturulmalıdır.
9. `LongClassRule` varsayılan threshold ile oluşturulmalıdır.
10. Analyzer gerçek bir `FileScanner` içermelidir.
11. Analyzer gerçek bir `SourceReader` içermelidir.
12. Analyzer gerçek bir `AnalysisEngine` içermelidir.
13. Engine altı varsayılan kuralı içermelidir.
14. Her analyzer çağrısı bağımsız bileşenler üretmelidir.
15. Oluşturulan analyzer küçük bir projeyi uçtan uca analiz edebilmelidir.
16. Alt bileşenlerden gelen hatalar değiştirilmemelidir.
17. Factory terminal çıktısı üretmemelidir.

### 21.13 Planlanan Test Senaryoları

- Varsayılan kuralların tuple olarak döndürülmesi
- Tam olarak altı kural oluşturulması
- Beklenen kural sınıflarının kullanılması
- Kural kimliklerinin kararlı sırada olması
- Her çağrıda yeni tuple oluşturulması
- Her çağrıda yeni kural nesneleri oluşturulması
- Long function varsayılan threshold değeri
- Long class varsayılan threshold değeri
- Gerçek `ProjectAnalyzer` oluşturulması
- Gerçek `FileScanner` kullanılması
- Gerçek `SourceReader` kullanılması
- Gerçek `AnalysisEngine` kullanılması
- Engine içerisinde varsayılan kuralların bulunması
- Ayrı analyzer çağrılarının bağımsız olması
- Geçici proje üzerinde uçtan uca analiz
- Var olmayan hedef hatasının iletilmesi

## 22. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Teknik Tasarım](technical-design.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)