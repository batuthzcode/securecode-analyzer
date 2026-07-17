# Analiz Dokümanı

## 1. Dokümanın Amacı

Bu dokümanın amacı, Python projelerinde temel statik kod analizi ve bağımlılık güvenlik taraması gerçekleştirecek araçların gereksinimlerini tanımlamaktır.

Proje iki temel analiz aracı, bu araçların üzerinde çalıştırılacağı örnek bir web uygulaması ve araçları otomatik olarak çalıştıracak bir CI/CD sürecinden oluşacaktır.

## 2. Sistem Kullanıcıları

### 2.1. Yazılım Geliştirici

Yazdığı Python kodunu analiz ederek kod kalitesi problemlerini tespit eder.

### 2.2. DevOps Ekibi

Analiz araçlarını CI/CD pipeline içerisinde çalıştırır ve belirlenen önem seviyesinin üzerindeki problemlerde pipeline'ın başarısız olmasını sağlar.

### 2.3. Güvenlik Ekibi

Projede kullanılan bağımlılıkların bilinen güvenlik açıklarını incelemek için bağımlılık tarama sonuçlarını kullanır.

### 2.4. Proje Yöneticisi veya Reviewer

Pull Request sırasında analiz sonuçlarını inceleyerek kodun ana branch'e alınıp alınmayacağına karar verir.

## 3. Fonksiyonel Gereksinimler

### FR-01 — Kaynak dizinin belirtilmesi

Kullanıcı, analiz edilecek Python projesinin dizinini komut satırı üzerinden belirtebilmelidir.

### FR-02 — Python dosyalarının bulunması

Statik analiz aracı, verilen dizin ve alt dizinlerde bulunan `.py` uzantılı dosyaları bulabilmelidir.

### FR-03 — Hariç tutulan dizinler

Araç aşağıdaki gibi analiz edilmemesi gereken dizinleri atlayabilmelidir:

* `.git`
* `.venv`
* `venv`
* `__pycache__`
* `.pytest_cache`

### FR-04 — Statik analiz kurallarının çalıştırılması

Araç, bulunan Python dosyaları üzerinde aktif statik analiz kurallarını çalıştırabilmelidir.

### FR-05 — TODO ve FIXME tespiti

Araç, kaynak kod içerisinde bulunan `TODO` ve `FIXME` ifadelerini raporlayabilmelidir.

### FR-06 — Uzun fonksiyon tespiti

Araç, belirlenen satır sayısı sınırını aşan fonksiyon ve metotları tespit edebilmelidir.

### FR-07 — Boş except bloğu tespiti

Araç, yalnızca `pass` içeren veya hiçbir işlem yapmayan `except` bloklarını tespit edebilmelidir.

### FR-08 — İsimlendirme kontrolü

Araç, fonksiyon ve sınıf isimlerinin belirlenen Python isimlendirme kurallarına uygunluğunu kontrol edebilmelidir.

Fonksiyonlar için `snake_case`, sınıflar için `PascalCase` kullanılması beklenmektedir.

### FR-09 — Hardcoded secret tespiti

Araç, kaynak kod içerisinde sabit olarak yazılmış olabilecek parola, API anahtarı, erişim anahtarı ve bağlantı bilgilerini tespit edebilmelidir.

### FR-10 — Bulgu bilgileri

Her statik analiz bulgusu aşağıdaki bilgileri içermelidir:

* Kural kimliği
* Kural adı
* Dosya yolu
* Satır numarası
* Önem seviyesi
* Problem açıklaması
* Çözüm önerisi

### FR-11 — Terminal çıktısı

Analiz sonuçları okunabilir şekilde terminalde gösterilebilmelidir.

### FR-12 — JSON çıktısı

Kullanıcı istediğinde analiz sonuçları JSON dosyasına yazılabilmelidir.

### FR-13 — Exit code üretimi

Araç, analiz sonucuna göre işletim sistemine uygun bir exit code döndürmelidir.

Önerilen exit code değerleri:

* `0`: Analiz başarılı ve eşik üzeri bulgu yok
* `1`: Belirlenen önem eşiğinin üzerinde bulgu var
* `2`: Kullanıcı girdisi veya yapılandırma hatası var
* `3`: Beklenmeyen çalışma hatası oluştu

### FR-14 — Requirements dosyasının okunması

Bağımlılık tarama aracı, verilen `requirements.txt` dosyasını okuyabilmelidir.

### FR-15 — Paket ve sürüm bilgisinin ayrıştırılması

Araç, bağımlılık satırlarından paket adı ve sürüm bilgisini çıkarabilmelidir.

İlk sürümde öncelikle aşağıdaki sabit sürüm formatı desteklenecektir:

```text
package-name==1.2.3
```

### FR-16 — Güvenlik verisi sorgulama

Araç, bağımlılıkları gerçek bir güvenlik açığı veri kaynağıyla karşılaştırabilmelidir.

Ana veri kaynağı olarak OSV kullanılacaktır. Testlerde gerçek kaynaklardan alınmış yerel JSON verileri kullanılabilecektir.

### FR-17 — Güvenlik açığı eşleştirme

Araç, kullanılan paket sürümünün bilinen bir güvenlik açığından etkilenip etkilenmediğini belirleyebilmelidir.

### FR-18 — Bağımlılık bulguları

Her bağımlılık güvenlik bulgusu aşağıdaki bilgileri içermelidir:

* Paket adı
* Kullanılan sürüm
* CVE veya advisory kimliği
* Açıklama
* Önem seviyesi
* Etkilenen sürüm bilgisi
* Güvenli veya önerilen sürüm
* Veri kaynağı

### FR-19 — Örnek uygulamanın analiz edilmesi

Her iki araç da örnek Python web uygulaması üzerinde çalıştırılabilmelidir.

### FR-20 — CI/CD entegrasyonu

Araçlar GitHub Actions içerisinde komut satırı üzerinden çalıştırılabilmelidir.

### FR-21 — Pipeline başarısızlık koşulu

Belirlenen önem seviyesinin üzerinde statik analiz veya güvenlik bulgusu tespit edildiğinde pipeline başarısız olabilmelidir.

### FR-22 — Aracın kendi kodunu analiz etmesi

Statik analiz aracı, kendi kaynak kodu üzerinde çalıştırılmalı ve sonuçları kontrol edilmelidir.

## 4. Fonksiyonel Olmayan Gereksinimler

### NFR-01 — Python sürümü

Proje Python 3.11 veya daha güncel bir sürümle çalışmalıdır.

### NFR-02 — Modülerlik

Statik analiz kuralları, raporlama sistemi, dosya tarayıcı ve bağımlılık tarayıcı birbirinden ayrılmış modüller halinde geliştirilmelidir.

### NFR-03 — Test edilebilirlik

Temel bileşenler bağımsız olarak unit testlerle test edilebilmelidir.

### NFR-04 — Anlaşılabilirlik

Kod, açıklayıcı sınıf ve fonksiyon isimleriyle yazılmalıdır. Karmaşık bölümlerde kısa açıklamalar veya docstring kullanılmalıdır.

### NFR-05 — Hata toleransı

Tek bir Python dosyasındaki syntax hatası, mümkünse bütün analiz işlemini durdurmamalıdır. Hatalı dosya raporlanmalı ve diğer dosyaların analizi devam etmelidir.

### NFR-06 — Güvenlik verisinin doğruluğu

CVE ve advisory verileri uydurulmamalı ve yapay zekâ tarafından üretilmemelidir.

Veriler OSV, GitHub Advisory Database veya NVD gibi gerçek kaynaklardan alınmalıdır.

### NFR-07 — Gizli verilerin korunması

Hardcoded secret tespit edildiğinde gizli değerin tamamı terminal veya JSON raporunda gösterilmemelidir.

### NFR-08 — Taşınabilirlik

Araç Windows ve Linux ortamlarında çalışabilecek şekilde geliştirilmelidir.

### NFR-09 — CI uyumluluğu

Araçlar kullanıcı etkileşimi gerektirmeden komut satırından çalışabilmelidir.

### NFR-10 — Performans

Araç, küçük ve orta boyutlu örnek Python projelerini kabul edilebilir sürede analiz edebilmelidir.

Bu proje için yüksek ölçekli performans optimizasyonu birincil hedef değildir.

### NFR-11 — Genişletilebilirlik

Yeni statik analiz kuralları, mevcut çekirdek yapıyı büyük ölçüde değiştirmeden eklenebilmelidir.

### NFR-12 — Dokümantasyon

Kurulum, kullanım, test ve örnek komutlar README veya `docs` klasöründe açıklanmalıdır.

## 5. Statik Analiz Kuralları

| Kural                         | Yaklaşım         | Tercih Nedeni                                                                               |
| ----------------------------- | ---------------- | ------------------------------------------------------------------------------------------- |
| TODO/FIXME tespiti            | Metin veya regex | Yorum satırlarında belirli ifadelerin aranması yeterlidir.                                  |
| Uzun fonksiyon                | AST              | Fonksiyonun gerçek başlangıç ve bitiş satırlarını güvenilir biçimde bulmak gerekir.         |
| Uzun sınıf                    | AST              | Sınıf sınırlarını ve içeriğini yapısal olarak incelemek gerekir.                            |
| Boş except bloğu              | AST              | `except` bloğunun gövdesindeki düğümlerin incelenmesi gerekir.                              |
| Fonksiyon isimlendirmesi      | AST ve regex     | AST ile fonksiyon adı bulunur, regex ile isim formatı kontrol edilir.                       |
| Sınıf isimlendirmesi          | AST ve regex     | AST ile sınıf adı bulunur, regex ile PascalCase kontrol edilir.                             |
| Hardcoded secret              | AST ve regex     | Şüpheli değişken isimleri regex ile, atanan sabit string değeri AST ile incelenir.          |
| Geniş exception yakalama      | AST              | `except Exception` veya çıplak `except` yapıları AST ile güvenilir biçimde bulunur.         |
| Kullanılmayan import          | AST              | Import ve isim kullanım ilişkilerinin incelenmesi gerekir.                                  |
| Tehlikeli fonksiyon kullanımı | AST              | `eval`, `exec` ve benzeri çağrıların gerçek fonksiyon çağrısı olup olmadığı incelenmelidir. |

İlk sürümde öncelikli kurallar:

1. TODO/FIXME tespiti
2. Uzun fonksiyon tespiti
3. Boş except bloğu tespiti
4. İsimlendirme kontrolü
5. Hardcoded secret tespiti

## 6. CVE Tarama Yaklaşımı

### 6.1. Alternatif 1 — Yerel JSON dosyası

Gerçek kaynaklardan alınan güvenlik açığı kayıtları proje içerisinde JSON dosyası olarak saklanabilir.

Avantajları:

* Testlerde internet bağlantısı gerekmez.
* Sonuçlar tekrarlanabilir olur.
* CI/CD süreci dış servislere bağımlı olmaz.

Dezavantajları:

* Veriler zamanla güncelliğini kaybeder.
* Manuel güncelleme gerekir.
* Sınırlı sayıda paketi kapsar.

### 6.2. Alternatif 2 — OSV API

Paket adı ve sürüm bilgisi OSV API'ye gönderilerek güncel güvenlik açıkları sorgulanabilir.

Avantajları:

* Gerçek ve güncel veri kullanılabilir.
* Çok sayıda paket desteklenebilir.
* Manuel veri yönetimi azalır.

Dezavantajları:

* İnternet bağlantısı gerekir.
* Servis erişilemez durumda olabilir.
* Testler dış servise bağımlı hale gelebilir.

### 6.3. Alternatif 3 — Hibrit yaklaşım

Normal kullanımda OSV API kullanılır. Unit testlerde ve çevrimdışı durumlarda gerçek kaynaklardan alınmış yerel test verileri kullanılır.

### 6.4. Seçilen yaklaşım

Hibrit yaklaşım seçilmiştir.

Seçim nedenleri:

* Normal kullanımda güncel güvenlik verisi sağlar.
* Unit testlerin internet bağlantısından bağımsız çalışmasını sağlar.
* CI/CD sürecinin daha kararlı olmasına yardımcı olur.
* Gerçek veri kullanma kuralına uyulmasını sağlar.

## 7. Girdi Formatları

### 7.1. Statik analiz girdisi

* Analiz edilecek klasör yolu
* Çıktı formatı
* Rapor dosyası yolu
* Başarısızlık önem eşiği
* Hariç tutulacak klasörler

Örnek kullanım:

```text
python -m static_analyzer.cli ./sample_app --format json --output reports/static.json --fail-on high
```

### 7.2. Bağımlılık tarama girdisi

* `requirements.txt` dosyasının yolu
* Çıktı formatı
* Rapor dosyası yolu
* Başarısızlık önem eşiği
* Veri kaynağı seçimi

Örnek kullanım:

```text
python -m dependency_scanner.cli sample_app/requirements.txt --format json --output reports/dependencies.json --fail-on critical
```

## 8. Çıktı Formatları

### 8.1. Terminal çıktısı

Terminal çıktısı kullanıcı tarafından okunabilir ve kısa olmalıdır.

Örnek:

```text
[HIGH] SEC001 sample.py:12 Hardcoded password detected.
Recommendation: Read the value from an environment variable.
```

### 8.2. JSON çıktısı

Örnek statik analiz çıktısı:

```json
{
  "tool": "static-analyzer",
  "target": "sample_app",
  "findings": [
    {
      "rule_id": "SEC001",
      "rule_name": "hardcoded-secret",
      "file_path": "sample_app/app.py",
      "line_number": 12,
      "severity": "high",
      "message": "Possible hardcoded password detected.",
      "recommendation": "Read the value from an environment variable."
    }
  ]
}
```

## 9. Hata Senaryoları

### ERR-01 — Kaynak dizin bulunamadı

Araç anlaşılır bir hata mesajı göstermeli ve uygun exit code ile kapanmalıdır.

### ERR-02 — Dosya okuma hatası

Dosya izinleri veya karakter kodlaması nedeniyle okunamayan dosya raporlanmalıdır.

### ERR-03 — Python syntax hatası

AST oluşturulamayan dosya raporlanmalı, mümkünse diğer dosyaların analizi devam etmelidir.

### ERR-04 — Requirements dosyası bulunamadı

Bağımlılık tarayıcı kullanıcıya dosyanın bulunamadığını bildirmelidir.

### ERR-05 — Hatalı requirements satırı

Desteklenmeyen veya hatalı bağımlılık satırı kontrollü şekilde raporlanmalıdır.

### ERR-06 — OSV servisine erişilemiyor

Araç bağlantı hatasını açıkça bildirmeli ve yapılandırmaya göre yerel veriye geçmeli veya kontrollü şekilde sonlanmalıdır.

### ERR-07 — Geçersiz çıktı yolu

Raporun yazılamadığı durum kullanıcıya bildirilmelidir.

### ERR-08 — Bilinmeyen önem seviyesi

Geçersiz `--fail-on` değeri kullanıcı hatası olarak raporlanmalıdır.

## 10. Kabul Kriterleri

### AC-01

Geçerli bir Python klasörü verildiğinde araç `.py` dosyalarını bulmalıdır.

### AC-02

TODO veya FIXME içeren bir dosyada doğru dosya ve satır numarasıyla bulgu üretilmelidir.

### AC-03

Belirlenen sınırı aşan bir fonksiyon doğru şekilde tespit edilmelidir.

### AC-04

Yalnızca `pass` içeren bir except bloğu raporlanmalıdır.

### AC-05

Temiz kod örneklerinde ilgili kurallar yanlış bulgu üretmemelidir.

### AC-06

Bulgular terminalde görüntülenebilmeli ve JSON dosyasına yazılabilmelidir.

### AC-07

Belirlenen önem eşiğinin üzerindeki bulguda araç başarısız exit code döndürmelidir.

### AC-08

Sabit sürüm içeren bir `requirements.txt` satırı doğru şekilde ayrıştırılmalıdır.

### AC-09

Gerçek bir advisory kaydıyla eşleşen bağımlılık doğru kimlik ve kaynak bilgisiyle raporlanmalıdır.

### AC-10

Güvenlik açığı bulunmayan bir bağımlılık için yanlış güvenlik bulgusu üretilmemelidir.

### AC-11

Unit testler GitHub Actions içerisinde başarıyla çalışmalıdır.

### AC-12

Statik analiz aracı kendi kaynak kodu üzerinde çalıştırılabilmelidir.

## 11. Varsayımlar ve Sınırlamalar

* İlk sürüm yalnızca Python kaynak kodunu analiz edecektir.
* İlk bağımlılık parser sürümü ağırlıklı olarak `paket==sürüm` formatını destekleyecektir.
* CVE ve advisory verileri yalnızca gerçek kaynaklardan alınacaktır.
* Önem seviyesi her veri kaynağında aynı şekilde bulunmayabilir.
* OSV sonuçlarında her zaman doğrudan güvenli sürüm bilgisi bulunmayabilir.
* İlk sürüm gelişmiş veri akışı veya kontrol akışı analizi yapmayacaktır.
* Hardcoded secret kuralı bazı false positive sonuçlar üretebilir.
