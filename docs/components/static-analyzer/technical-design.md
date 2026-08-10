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
        └── base.py

tests/
├── test_models.py
└── test_base_rule.py
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

Kural arayüzlerinin paket dışından daha düzenli şekilde kullanılmasını sağlar.

Bu yapı sayesinde aşağıdaki import kullanılabilir:

```python
from static_analyzer.rules import BaseRule
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

Planlanan AST tabanlı kurallar:

- Uzun fonksiyon tespiti
- Uzun sınıf tespiti
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

Bu karar, ilk gerçek analiz kuralı ve çıktı katmanı geliştirilirken
netleştirilecektir.

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

Projede otomatik testler için `pytest` kullanılmaktadır.

Mevcut unit testler aşağıdaki davranışları doğrulamaktadır:

- `Finding.to_dict()` metodunun serileştirilebilir veri döndürmesi
- `Finding` modelinin varsayılan olarak `WARNING` önem seviyesini kullanması
- Soyut `BaseRule` sınıfının doğrudan oluşturulamaması
- Somut bir kuralın `check()` sözleşmesini uygulayabilmesi

Bütün testler aşağıdaki komutla çalıştırılabilir:

```bash
python -m pytest -v
```

Mevcut durumda dört unit test bulunmaktadır ve dört test de başarılı şekilde
çalışmaktadır.

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
doğrudan AST yapısına dönüştürülebilecektir. Böylece testler için gereksiz
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

Prototip kodunun sorumlulukları, geliştirilecek gerçek kural sınıflarına,
analiz motoruna ve çıktı katmanına ayrılacaktır. Böylece tek dosyada bulunan
deneme kodu yerine test edilebilir ve genişletilebilir modüler bir yapı
oluşturulacaktır.

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

Henüz tamamlanmayan çalışmalar:

- Dosya bulma ve klasör tarama mekanizması
- Kaynak kod okuma ve parse etme servisi
- Analiz motoru
- Kural kayıt mekanizması
- Gerçek analiz kuralları
- Metin tabanlı kural arayüzü
- Terminal çıktı biçimlendiricisi
- JSON çıktı katmanı
- CLI komutları
- Exit code politikası
- Aracın kendi kaynak kodunu analiz etmesi
- CI/CD entegrasyonu

## 13. Gelecek Geliştirmeler

Planlanan sonraki geliştirmeler:

- İlk somut AST tabanlı analiz kuralının geliştirilmesi
- Uzun fonksiyon kuralının hazırlanması
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
