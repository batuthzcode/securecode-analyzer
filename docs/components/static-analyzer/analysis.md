# Static Code Analyzer - Analiz

## 1. Amaç

Static Code Analyzer bileşeninin amacı, Python kaynak kodlarını çalıştırmadan
inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit etmektir.

Araç, tespit ettiği problemlerin doğrudan hata olduğunu iddia etmek yerine
geliştirici tarafından incelenmesi gereken bulgular üretecektir.

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
10. Kritik veya yapılandırılmış eşik üzerindeki bulgular için başarısız exit
    code üretebilmelidir.
11. Aynı dosyada birden fazla bulgu üretebilmelidir.
12. Bir dosyadaki hata mümkünse diğer dosyaların analizini durdurmamalıdır.

## 5. Planlanan Analiz Kuralları

| Kural | Yaklaşım | Gerekçe |
|---|---|---|
| Uzun fonksiyon | AST | Fonksiyon başlangıç ve bitiş satırları yapısal olarak incelenir |
| Uzun sınıf | AST | Gerçek sınıf tanımlarının ve satır aralıklarının bulunması gerekir |
| Boş `except` bloğu | AST | Gerçek exception blokları incelenmelidir |
| Fonksiyon isimlendirme | AST | Fonksiyon tanımlarının isimleri kontrol edilir |
| Sınıf isimlendirme | AST | Sınıf tanımlarının isimleri kontrol edilir |
| `TODO` ve `FIXME` | Satır taraması | Yorumlar AST içerisinde doğrudan korunmaz |
| Hardcoded secret | Regex ve metin analizi | Şüpheli anahtar ve değer desenleri aranır |
| Bağlantı adresi | Regex ve metin analizi | Kaynak kod içerisindeki bağlantı desenleri aranır |

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
incelenmesi gereken bir kod kalitesi bulgusu üretecektir.

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

Bu kural Python'ın yerleşik `ast` modülünü kullanacaktır.

AST tercih edilmesinin nedenleri:

- Gerçek fonksiyon tanımlarının güvenilir şekilde bulunabilmesi
- Normal ve asenkron fonksiyonların tespit edilebilmesi
- Yorum veya string içerisindeki `def` ifadelerinin dikkate alınmaması
- Fonksiyonların başlangıç ve bitiş satırlarının alınabilmesi
- İç içe tanımlanan fonksiyonların ayrı ayrı incelenebilmesi

Kural aşağıdaki AST düğümlerini kontrol edecektir:

- `ast.FunctionDef`
- `ast.AsyncFunctionDef`

### 6.4 Fonksiyon Uzunluğu Hesaplaması

Fonksiyon uzunluğu aşağıdaki AST bilgileri kullanılarak hesaplanacaktır:

- `lineno`: fonksiyon tanımının başladığı satır
- `end_lineno`: fonksiyon tanımının bittiği satır

Hesaplama:

```text
fonksiyon uzunluğu = bitiş satırı - başlangıç satırı + 1
```

`end_lineno` bilgisinin bulunmadığı durumda başlangıç satırı kullanılacaktır.

İlk sürümde başlangıç ve bitiş satırları arasındaki toplam fiziksel satır
sayısı dikkate alınacaktır.

### 6.5 Varsayılan Eşik Değeri

İlk sürümde varsayılan eşik:

```text
50 satır
```

Fonksiyon uzunluğu eşik değerinden büyük olduğunda bulgu üretilecektir.

Örnek davranış:

- 49 satırlık fonksiyon bulgu üretmez.
- 50 satırlık fonksiyon bulgu üretmez.
- 51 satırlık fonksiyon bulgu üretir.

Eşik değerinin daha sonra CLI veya yapılandırma dosyası üzerinden
değiştirilebilir olması planlanmaktadır.

### 6.6 Önem Seviyesi

Uzun fonksiyon bulgularının varsayılan önem seviyesi `WARNING` olacaktır.

Bu seviye seçilmiştir çünkü uzun fonksiyon:

- Doğrudan bir güvenlik açığı değildir.
- Her zaman çalışma zamanı hatasına neden olmaz.
- Kodun okunabilirliğini azaltabilir.
- Unit test yazılmasını zorlaştırabilir.
- Fonksiyonun birden fazla sorumluluk taşıdığına işaret edebilir.
- Bakım maliyetini artırabilir.

### 6.7 Üretilecek Bulgu

Kural, eşik değerini aşan her fonksiyon için bir `Finding` nesnesi
döndürecektir.

Bulgu aşağıdaki alanları içerecektir:

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

Örnek bulgu:

```json
{
  "rule_id": "SA001",
  "message": "Function 'process_data' has 64 lines, exceeding the limit of 50.",
  "file_path": "example.py",
  "line_number": 12,
  "severity": "warning",
  "column_number": 0
}
```

### 6.8 Normal ve Asenkron Fonksiyonlar

Kural hem normal hem de asenkron fonksiyonları kontrol etmelidir.

Normal fonksiyon örneği:

```python
def process_data():
    pass
```

Asenkron fonksiyon örneği:

```python
async def fetch_data():
    pass
```

Her iki fonksiyon türü için aynı uzunluk hesaplama yöntemi kullanılacaktır.

### 6.9 İç İçe Fonksiyonlar

Başka bir fonksiyon içerisinde tanımlanan fonksiyonlar da ayrı bir fonksiyon
olarak değerlendirilecektir.

Örnek:

```python
def outer_function():
    def inner_function():
        pass
```

`outer_function` ve `inner_function` kendi başlangıç ve bitiş satırlarına göre
ayrı ayrı kontrol edilecektir.

### 6.10 Kabul Kriterleri

Uzun fonksiyon kuralı aşağıdaki koşulları sağlamalıdır:

1. Normal Python fonksiyonlarını tespit etmelidir.
2. Asenkron Python fonksiyonlarını tespit etmelidir.
3. Eşik değerini aşan fonksiyon için bulgu üretmelidir.
4. Eşik değerine eşit fonksiyon için bulgu üretmemelidir.
5. Eşik değerinden kısa fonksiyon için bulgu üretmemelidir.
6. Özel bir eşik değeriyle çalışabilmelidir.
7. Bulgunun kural kimliği `SA001` olmalıdır.
8. Bulgunun önem seviyesi `WARNING` olmalıdır.
9. Bulgunun dosya yolu doğru olmalıdır.
10. Bulgunun satır numarası fonksiyonun başlangıç satırı olmalıdır.
11. Bulgunun sütun numarası AST düğümünden alınmalıdır.
12. Bulgu mesajı fonksiyon adını içermelidir.
13. Bulgu mesajı mevcut fonksiyon uzunluğunu içermelidir.
14. Bulgu mesajı yapılandırılmış eşik değerini içermelidir.
15. Birden fazla uzun fonksiyon için ayrı bulgular üretilmelidir.
16. İç içe fonksiyonlar ayrı ayrı kontrol edilmelidir.

### 6.11 Test Senaryoları

Aşağıdaki unit test senaryoları hazırlanacaktır:

- Kısa normal fonksiyon bulgu üretmez.
- Uzun normal fonksiyon bulgu üretir.
- Kısa asenkron fonksiyon bulgu üretmez.
- Uzun asenkron fonksiyon bulgu üretir.
- Eşik değerine eşit fonksiyon bulgu üretmez.
- Özel eşik değeri kullanıldığında davranış değişir.
- Birden fazla uzun fonksiyon ayrı bulgular üretir.
- İç içe uzun fonksiyon ayrıca bulgu üretir.
- Bulgu doğru kural kimliğini içerir.
- Bulgu doğru dosya yolunu içerir.
- Bulgu doğru satır numarasını içerir.
- Bulgu doğru sütun numarasını içerir.
- Bulgu doğru önem seviyesini içerir.
- Bulgu mesajı gerekli bilgileri içerir.

### 6.12 Kapsam Dışı Durumlar

İlk sürümde aşağıdaki konular uzun fonksiyon kuralının kapsamı dışında
tutulacaktır:

- Boş satırların hesaplamadan çıkarılması
- Yorum satırlarının hesaplamadan çıkarılması
- Docstring satırlarının hesaplamadan çıkarılması
- Fonksiyon karmaşıklığının ölçülmesi
- Fonksiyonun yaptığı iş sayısının değerlendirilmesi
- Fonksiyonun otomatik olarak parçalara ayrılması
- Refactoring önerisinin otomatik uygulanması
- Decorator satırlarının fonksiyon uzunluğuna eklenmesi

Bu ihtiyaçlar daha sonraki sürümlerde ayrıca değerlendirilebilir.

## 7. Çıktı Gereksinimleri

Her bulgu için aşağıdaki bilgilerin üretilmesi beklenmektedir:

- Kural kimliği
- Kural adı
- Dosya yolu
- Satır numarası
- Varsa sütun numarası
- Önem seviyesi
- Problem açıklaması
- Çözüm önerisi

Mevcut `Finding` modelinde aşağıdaki alanlar bulunmaktadır:

- `rule_id`
- `message`
- `file_path`
- `line_number`
- `severity`
- `column_number`

Kural adı ve çözüm önerisinin hangi katmanda tutulacağı, raporlama bileşeni
geliştirilirken netleştirilecektir.

Sonuçlar ilk aşamada terminalde gösterilecek, daha sonra JSON formatında
kaydedilebilecektir.

## 8. Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır hata mesajlarıyla bildirilmelidir:

- Dosyanın bulunamaması
- Dosyanın okunamaması
- Geçersiz dosya uzantısı verilmesi
- Python sözdizimi hatası bulunması
- Geçersiz dosya veya klasör yolu verilmesi
- Boş klasör verilmesi
- Kaynak dosyanın UTF-8 olarak okunamaması
- Analiz kuralının beklenmeyen hata üretmesi

Bir dosyada hata oluşması durumunda mümkünse diğer dosyaların analizi devam
etmelidir.

## 9. Fonksiyonel Olmayan Gereksinimler

### 9.1 Genişletilebilirlik

Yeni analiz kuralları mevcut kurallar değiştirilmeden eklenebilmelidir.

### 9.2 Test Edilebilirlik

Her analiz kuralı bağımsız unit testlerle doğrulanabilmelidir.

### 9.3 Okunabilirlik

Kod, anlaşılır sınıf ve fonksiyon isimleriyle geliştirilmelidir. Kamuya açık
sınıf ve fonksiyonlar açıklayıcı docstring içermelidir.

### 9.4 Güvenlik

Analiz edilen kaynak kod çalıştırılmamalıdır. Kaynak kod yalnızca metin ve AST
yapısı üzerinden incelenmelidir.

### 9.5 Taşınabilirlik

Araç Windows, Linux ve macOS ortamlarında çalışabilecek şekilde
geliştirilmelidir.

### 9.6 Performans

Her Python dosyası AST tabanlı kurallar için mümkün olduğunca yalnızca bir kez
parse edilmelidir.

## 10. Mevcut Durum

Tamamlanan çalışmalar:

- Statik analiz paket yapısı oluşturuldu.
- `Severity` enum yapısı oluşturuldu.
- `Finding` veri modeli oluşturuldu.
- Bulguların sözlük formatına dönüştürülmesi sağlandı.
- AST tabanlı kurallar için `BaseRule` arayüzü oluşturuldu.
- Veri modeli ve kural arayüzü unit testleri eklendi.
- Python geliştirme ve test ortamı yapılandırıldı.
- Teknik tasarım dokümanı güncellendi.
- `LongFunctionRule` sınıfı geliştirildi.
- Normal ve asenkron fonksiyon desteği eklendi.
- İç içe fonksiyonların ayrı ayrı kontrol edilmesi sağlandı.
- Yapılandırılabilir satır sınırı eklendi.
- Geçersiz eşik değerleri için doğrulama eklendi.
- Uzun fonksiyon kuralı 10 test senaryosuyla doğrulandı.

Henüz tamamlanmayan çalışmalar:

- Dosya ve klasör tarama mekanizması
- Analiz motoru
- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- CI/CD entegrasyonu

## 11. Navigation

- [Static Code Analyzer sayfasına dön](README.md)
- [Teknik Tasarım](technical-design.md)
- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)