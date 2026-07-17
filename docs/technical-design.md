# Teknik Tasarım Dokümanı

## 1. Dokümanın Amacı

Bu doküman, Python projelerinde temel statik kod analizi ve bağımlılık güvenlik taraması gerçekleştirecek araçların teknik tasarımını açıklamaktadır.

Dokümanda sistem mimarisi, kullanılan teknolojiler, klasör yapısı, modüllerin sorumlulukları, veri modelleri, komut satırı tasarımı, CVE tarama yaklaşımı, test stratejisi ve CI/CD pipeline akışı tanımlanmıştır.

## 2. Sistem Genel Bakışı

Proje dört ana bileşenden oluşacaktır:

1. Statik kod analiz aracı
2. Bağımlılık ve CVE tarama aracı
3. Örnek Python web uygulaması
4. GitHub Actions CI/CD pipeline

Statik analiz aracı Python kaynak kodlarını inceleyerek kod kalitesi ve temel güvenlik problemlerini tespit edecektir.

Bağımlılık tarama aracı, `requirements.txt` dosyasındaki paket ve sürüm bilgilerini okuyarak bunları gerçek güvenlik açığı verileriyle karşılaştıracaktır.

Örnek web uygulaması, iki analiz aracının çalışmasını göstermek için kullanılacaktır.

GitHub Actions pipeline ise testleri ve analiz araçlarını Pull Request süreçlerinde otomatik olarak çalıştıracaktır.

## 3. Sistem Mimarisi

Sistem aşağıdaki genel akışa sahip olacaktır:

```text
Kullanıcı veya GitHub Actions
            |
            v
         CLI Katmanı
            |
      +-----+------+
      |            |
      v            v
Statik Analiz   Bağımlılık Tarama
      |            |
      v            v
Kural Motoru    Requirements Parser
      |            |
      v            v
Dosya Tarama    OSV / Yerel Veri
      |            |
      +-----+------+
            |
            v
       Sonuç Modelleri
            |
      +-----+------+
      |            |
      v            v
 Terminal Çıktısı JSON Raporu
            |
            v
         Exit Code
```

CLI katmanı kullanıcının komutlarını alacaktır.

Analiz katmanları kaynak kodu veya bağımlılık dosyasını işleyecektir.

Bulunan problemler ortak veri modellerine dönüştürülecek ve raporlama katmanına gönderilecektir.

## 4. Kullanılacak Teknolojiler

### 4.1. Python

Projenin ana programlama dili Python olacaktır.

Seçim nedenleri:

* Python kaynak kodunu analiz etmek için yerleşik `ast` modülü bulunmaktadır.
* Komut satırı araçları geliştirmek kolaydır.
* Test ve web geliştirme araçları geniştir.
* Proje kapsamında analiz edilecek örnek uygulama da Python olacaktır.
* Öğrenme ve prototip geliştirme süresi diğer bazı dillere göre daha düşüktür.

Hedef Python sürümü:

```text
Python 3.11 veya üzeri
```

### 4.2. ast

Python kaynak kodunun Abstract Syntax Tree yapısına dönüştürülmesi için kullanılacaktır.

Kullanım alanları:

* Fonksiyonların bulunması
* Fonksiyon uzunluğunun hesaplanması
* Sınıfların bulunması
* Boş except bloklarının tespit edilmesi
* Fonksiyon ve sınıf isimlerinin kontrol edilmesi
* Sabit string atamalarının incelenmesi
* Tehlikeli fonksiyon çağrılarının bulunması

`ast` kullanılması, yalnızca metin eşleştirmeye göre Python kodunun yapısını daha güvenilir biçimde anlamayı sağlar.

### 4.3. re

Python’un yerleşik `re` modülü regex tabanlı kontroller için kullanılacaktır.

Kullanım alanları:

* TODO ve FIXME tespiti
* Fonksiyon isimlerinin `snake_case` formatında olup olmadığının kontrolü
* Sınıf isimlerinin `PascalCase` formatında olup olmadığının kontrolü
* Şüpheli secret değişken isimlerinin eşleştirilmesi

### 4.4. argparse

Komut satırı arayüzünün ilk sürümünde Python’un yerleşik `argparse` modülü kullanılacaktır.

Seçim nedenleri:

* Ek bağımlılık gerektirmez.
* Alt komutları ve parametreleri destekler.
* Otomatik yardım mesajı oluşturur.
* Başlangıç seviyesinde CLI geliştirmek için yeterlidir.

Alternatif olarak Typer veya Click kullanılabilir. Ancak ilk sürümde ek bağımlılığı azaltmak için `argparse` tercih edilmiştir.

### 4.5. dataclasses

Statik analiz ve güvenlik bulgularını temsil eden veri modellerinde kullanılacaktır.

Seçim nedenleri:

* Veri sınıflarını sade biçimde tanımlamayı sağlar.
* JSON dönüşümünü kolaylaştırır.
* Tekrarlanan constructor kodunu azaltır.
* Testlerde nesne karşılaştırmasını kolaylaştırır.

### 4.6. json

Analiz sonuçlarını JSON dosyasına yazmak ve yerel advisory verilerini okumak için kullanılacaktır.

### 4.7. pathlib

Dosya ve klasör yollarının yönetilmesi için kullanılacaktır.

Seçim nedenleri:

* Windows ve Linux arasında daha taşınabilir çalışır.
* Klasör tarama işlemlerini kolaylaştırır.
* Eski `os.path` kullanımına göre daha okunabilir bir yapı sağlar.

### 4.8. urllib veya httpx

OSV API ile HTTP iletişimi için kullanılacaktır.

İki alternatif bulunmaktadır:

* Python yerleşik `urllib`
* Harici `httpx` kütüphanesi

İlk prototipte bağımlılık sayısını azaltmak için `urllib` kullanılabilir. Daha anlaşılır hata yönetimi ve timeout desteği gerektiğinde `httpx` tercih edilebilir.

### 4.9. packaging

Python sürümlerinin güvenilir biçimde karşılaştırılması için `packaging` kütüphanesi kullanılacaktır.

Örnek:

```text
1.10.0 ile 1.9.0 sürümlerinin string olarak karşılaştırılması yanlış sonuç üretebilir.
```

Bu nedenle sürüm karşılaştırmasında normal metin karşılaştırması kullanılmayacaktır.

### 4.10. pytest

Unit ve entegrasyon testleri için kullanılacaktır.

Seçim nedenleri:

* Python projelerinde yaygın kullanılır.
* Basit test yazımına sahiptir.
* Fixture desteği sağlar.
* Geçici dosya ve klasör testlerini kolaylaştırır.
* GitHub Actions ile kolayca çalıştırılabilir.

### 4.11. Flask

Örnek web uygulaması için Flask kullanılacaktır.

Seçim nedenleri:

* Küçük CRUD uygulamaları için yeterlidir.
* Öğrenme maliyeti düşüktür.
* HTML template desteği bulunmaktadır.
* Projenin ana amacı web uygulaması değil analiz araçlarıdır.
* Minimum kod ile çalışan bir uygulama hazırlanabilir.

Alternatif olarak FastAPI kullanılabilir. Ancak örnek uygulamanın küçük tutulması için Flask tercih edilmiştir.

### 4.12. GitHub Actions

CI/CD pipeline için kullanılacaktır.

Seçim nedenleri:

* GitHub reposuyla doğrudan entegredir.
* Public repository için kullanılabilir.
* Pull Request sırasında otomatik test ve analiz çalıştırabilir.
* Harici bir CI/CD servisine ihtiyaç bırakmaz.

## 5. Proje Klasör Yapısı

Önerilen proje yapısı:

```text
python-security-analyzer/
|
|-- README.md
|-- pyproject.toml
|-- requirements-dev.txt
|-- .gitignore
|
|-- docs/
|   |-- scope.md
|   |-- analysis.md
|   |-- technical-design.md
|   `-- project-plan.md
|
|-- static_analyzer/
|   |-- __init__.py
|   |-- cli.py
|   |-- scanner.py
|   |-- models.py
|   |-- reporter.py
|   |-- config.py
|   `-- rules/
|       |-- __init__.py
|       |-- base.py
|       |-- todo_rule.py
|       |-- long_function_rule.py
|       |-- empty_except_rule.py
|       |-- naming_rule.py
|       `-- hardcoded_secret_rule.py
|
|-- dependency_scanner/
|   |-- __init__.py
|   |-- cli.py
|   |-- parser.py
|   |-- scanner.py
|   |-- models.py
|   |-- reporter.py
|   |-- osv_client.py
|   `-- data/
|       `-- advisories.json
|
|-- sample_app/
|   |-- app.py
|   |-- requirements.txt
|   |-- templates/
|   `-- static/
|
|-- examples/
|   `-- vulnerable_code.py
|
|-- tests/
|   |-- static_analyzer/
|   |-- dependency_scanner/
|   `-- sample_app/
|
`-- .github/
    `-- workflows/
        `-- ci.yml
```

## 6. Statik Analiz Aracı Modülleri

### 6.1. cli.py

Sorumlulukları:

* Komut satırı parametrelerini almak
* Kaynak dizini doğrulamak
* Çıktı formatını belirlemek
* Başarısızlık önem seviyesini almak
* Scanner bileşenini çalıştırmak
* Sonuçlara göre exit code üretmek

CLI doğrudan kural kontrolü yapmayacaktır. Yalnızca diğer bileşenleri yönetecektir.

### 6.2. scanner.py

Sorumlulukları:

* Verilen dizindeki Python dosyalarını bulmak
* Alt klasörleri taramak
* Hariç tutulan klasörleri atlamak
* Dosya içeriğini okumak
* Gerekli durumlarda AST oluşturmak
* Aktif kuralları çalıştırmak
* Bulguları bir listede toplamak
* Dosya okuma ve syntax hatalarını yönetmek

### 6.3. models.py

Sorumlulukları:

* Önem seviyelerini tanımlamak
* Statik analiz bulgu modelini tanımlamak
* Bulguları dictionary veya JSON formatına dönüştürmek

Önerilen önem seviyeleri:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

### 6.4. reporter.py

Sorumlulukları:

* Bulguları terminalde göstermek
* Bulguları JSON dosyasına yazmak
* Özet bilgisi üretmek
* Bulgu sayısını önem seviyesine göre gruplamak

### 6.5. config.py

Sorumlulukları:

* Varsayılan kural eşiklerini tanımlamak
* Hariç tutulan klasörleri tutmak
* Önem seviyelerinin sıralamasını tanımlamak

Örnek ayarlar:

```text
Maksimum fonksiyon uzunluğu: 30 satır
Maksimum sınıf uzunluğu: 200 satır
Varsayılan başarısızlık seviyesi: high
```

### 6.6. rules/base.py

Tüm statik analiz kurallarının uygulayacağı ortak arayüzü tanımlayacaktır.

Her kural aşağıdaki bilgileri taşımalıdır:

* Kural kimliği
* Kural adı
* Varsayılan önem seviyesi
* Kısa açıklama
* Çözüm önerisi
* Analiz metodu

Örnek tasarım:

```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseRule(ABC):
    rule_id: str
    rule_name: str

    @abstractmethod
    def analyze(self, file_path: Path, source: str):
        raise NotImplementedError
```

### 6.7. Kural modülleri

Her kural ayrı bir Python dosyasında bulunacaktır.

Bu tasarımın avantajları:

* Kurallar birbirinden bağımsız test edilebilir.
* Yeni kural eklemek kolaylaşır.
* Tek bir dosyanın aşırı büyümesi engellenir.
* Bir kuraldaki hata diğer kuralların kodunu doğrudan etkilemez.

## 7. Regex ve AST Tasarım Kararı

Her problem için aynı analiz yaklaşımı kullanılmayacaktır.

### 7.1. TODO/FIXME

Tercih edilen yöntem:

```text
Satır tabanlı metin arama veya regex
```

Neden:

* Aranan bilgi doğrudan metin içerisinde bulunur.
* Kod yapısının anlaşılması gerekmez.
* AST yorum satırlarını saklamaz.
* Regex yaklaşımı daha basit ve yeterlidir.

### 7.2. Uzun fonksiyon

Tercih edilen yöntem:

```text
AST
```

Neden:

* Fonksiyonun nerede başladığını ve bittiğini bilmek gerekir.
* İç içe fonksiyonlar bulunabilir.
* `def` kelimesini regex ile aramak güvenilir değildir.
* AST, fonksiyonun başlangıç ve bitiş satırlarını sağlayabilir.

### 7.3. Boş except bloğu

Tercih edilen yöntem:

```text
AST
```

Neden:

* `except` bloğunun gerçekten yalnızca `pass` içerip içermediği incelenmelidir.
* Yorum veya string içerisindeki `except` kelimeleri yanlış bulgu üretmemelidir.

### 7.4. İsimlendirme

Tercih edilen yöntem:

```text
AST ve regex
```

Neden:

* AST ile gerçek fonksiyon ve sınıf isimleri bulunur.
* Regex ile isimlerin `snake_case` veya `PascalCase` formatına uyup uymadığı kontrol edilir.

### 7.5. Hardcoded secret

Tercih edilen yöntem:

```text
AST ve regex
```

Neden:

* Regex ile `password`, `secret`, `api_key` ve `token` gibi şüpheli değişken isimleri bulunabilir.
* AST ile değişkene doğrudan sabit string atanıp atanmadığı kontrol edilebilir.
* `os.getenv()` gibi güvenli yaklaşımların yanlışlıkla raporlanması azaltılabilir.

## 8. Statik Analiz Veri Modeli

Önerilen bulgu modeli:

```python
from dataclasses import dataclass
from enum import Enum

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Finding:
    rule_id: str
    rule_name: str
    file_path: str
    line_number: int
    severity: Severity
    message: str
    recommendation: str
```

Her kural aynı veri modelini kullanacaktır.

Bu sayede raporlama katmanı hangi kuralın çalıştığını bilmek zorunda kalmadan sonuçları işleyebilecektir.

## 9. Statik Analiz İşlem Akışı

Statik analiz aşağıdaki sırayla çalışacaktır:

1. Kullanıcı kaynak dizini verir.
2. CLI parametreleri doğrular.
3. Scanner Python dosyalarını bulur.
4. Hariç tutulan klasörler atlanır.
5. Her dosyanın metin içeriği okunur.
6. AST gerektiren kurallar için `ast.parse()` çalıştırılır.
7. Aktif kurallar dosya üzerinde çalıştırılır.
8. Kurallar `Finding` nesneleri üretir.
9. Bütün bulgular bir araya getirilir.
10. Terminal veya JSON raporu oluşturulur.
11. Önem eşiğine göre exit code belirlenir.

## 10. Bağımlılık Tarayıcı Modülleri

### 10.1. cli.py

Sorumlulukları:

* Requirements dosya yolunu almak
* Çıktı formatını almak
* Başarısızlık önem seviyesini almak
* Veri kaynağı seçimini almak
* Tarama işlemini başlatmak
* Exit code üretmek

### 10.2. parser.py

Sorumlulukları:

* `requirements.txt` dosyasını okumak
* Boş satırları atlamak
* Yorum satırlarını atlamak
* Paket adı ve sürüm bilgisini ayırmak
* Desteklenmeyen formatları kontrollü biçimde raporlamak

İlk sürümde öncelikle şu format desteklenecektir:

```text
package-name==1.2.3
```

### 10.3. osv_client.py

Sorumlulukları:

* OSV API isteğini oluşturmak
* Paket adı ve sürüm bilgisini göndermek
* Timeout uygulamak
* HTTP ve bağlantı hatalarını yönetmek
* Gelen JSON cevabını okumak
* Sonucu iç veri modeline dönüştürmek

### 10.4. scanner.py

Sorumlulukları:

* Parser tarafından bulunan bağımlılıkları almak
* Her bağımlılık için advisory sorgulamak
* Etkilenen sürümleri kontrol etmek
* Güvenlik bulgularını oluşturmak
* Bütün sonuçları toplamak

### 10.5. models.py

Aşağıdaki modelleri içerecektir:

* Dependency
* Vulnerability
* DependencyFinding
* Severity

Önerilen bağımlılık modeli:

```python
from dataclasses import dataclass

@dataclass
class Dependency:
    name: str
    version: str
```

Önerilen güvenlik bulgusu modeli:

```python
@dataclass
class DependencyFinding:
    package_name: str
    installed_version: str
    advisory_id: str
    severity: str
    summary: str
    fixed_version: str | None
    source: str
```

### 10.6. reporter.py

Sorumlulukları:

* Güvenlik bulgularını terminalde göstermek
* JSON raporu oluşturmak
* Önem seviyesine göre özet üretmek

## 11. CVE Tarama Tasarımı

### 11.1. Seçilen yöntem

Hibrit CVE tarama yaklaşımı kullanılacaktır.

Normal kullanımda:

```text
OSV API
```

Unit testlerde:

```text
Gerçek kaynaktan alınmış yerel JSON test verileri
```

### 11.2. İşlem akışı

1. Kullanıcı `requirements.txt` dosyasını verir.
2. Parser paket ve sürüm bilgilerini çıkarır.
3. Paket adı normalize edilir.
4. Paket ve sürüm OSV API'ye gönderilir.
5. Gelen güvenlik kayıtları ayrıştırılır.
6. CVE veya advisory kimlikleri alınır.
7. Etkilenen sürüm bilgileri incelenir.
8. Düzeltilmiş sürüm bilgisi varsa rapora eklenir.
9. Bulgular terminal veya JSON formatında gösterilir.
10. Önem eşiğine göre exit code üretilir.

### 11.3. Güvenlik verisinin doğruluğu

CVE ve advisory bilgileri hiçbir durumda tahmin edilmeyecek veya yapay zekâ tarafından üretilmeyecektir.

Veriler yalnızca aşağıdaki gibi güvenilir kaynaklardan alınacaktır:

* OSV
* GitHub Advisory Database
* NVD

Yerel test verilerinde veri kaynağı ve advisory kimliği saklanacaktır.

## 12. Paket Sürümü Karşılaştırması

Sürüm karşılaştırmasında doğrudan string karşılaştırması kullanılmayacaktır.

Yanlış yaklaşım:

```python
"2.10.0" < "2.9.0"
```

Doğru yaklaşım:

```python
from packaging.version import Version

Version("2.10.0") > Version("2.9.0")
```

Bu yöntem Python paket sürümlerini daha güvenilir biçimde karşılaştırır.

## 13. CLI Komut Tasarımı

### 13.1. Statik analiz komutu

Örnek:

```text
python -m static_analyzer.cli ./sample_app
```

JSON raporu:

```text
python -m static_analyzer.cli ./sample_app --format json --output reports/static.json
```

Başarısızlık eşiği:

```text
python -m static_analyzer.cli ./sample_app --fail-on high
```

Planlanan parametreler:

| Parametre              | Açıklama                            |
| ---------------------- | ----------------------------------- |
| `target`               | Analiz edilecek dizin               |
| `--format`             | Terminal veya JSON çıktısı          |
| `--output`             | JSON rapor dosyasının yolu          |
| `--fail-on`            | Pipeline başarısızlık önem seviyesi |
| `--exclude`            | Hariç tutulacak klasörler           |
| `--max-function-lines` | Maksimum fonksiyon satır sayısı     |

### 13.2. Bağımlılık tarama komutu

Örnek:

```text
python -m dependency_scanner.cli sample_app/requirements.txt
```

JSON raporu:

```text
python -m dependency_scanner.cli sample_app/requirements.txt --format json --output reports/dependencies.json
```

Planlanan parametreler:

| Parametre      | Açıklama                            |
| -------------- | ----------------------------------- |
| `requirements` | Requirements dosyasının yolu        |
| `--format`     | Terminal veya JSON çıktısı          |
| `--output`     | Rapor dosyasının yolu               |
| `--fail-on`    | Pipeline başarısızlık önem seviyesi |
| `--source`     | OSV veya yerel veri kaynağı         |
| `--timeout`    | API zaman aşımı süresi              |

## 14. Exit Code Tasarımı

İki araç için ortak exit code yaklaşımı kullanılacaktır:

| Exit code | Anlamı                                      |
| --------- | ------------------------------------------- |
| `0`       | İşlem başarılı, eşik üzerinde bulgu yok     |
| `1`       | Eşik üzerinde bulgu bulundu                 |
| `2`       | Kullanıcı girdisi veya konfigürasyon hatası |
| `3`       | Beklenmeyen çalışma hatası                  |
| `4`       | Harici güvenlik servisine erişim hatası     |

CI/CD pipeline bu kodları kullanarak işlemin başarılı veya başarısız olduğuna karar verecektir.

## 15. Örnek Web Uygulaması Tasarımı

Örnek uygulama basit bir görev takip uygulaması olacaktır.

### 15.1. Özellikler

* Görevleri listeleme
* Yeni görev ekleme
* Görev güncelleme
* Görev silme
* Görevi tamamlandı olarak işaretleme
* Verileri bellekte saklama
* Basit HTML arayüzü

### 15.2. Endpointler

| HTTP metodu | Endpoint      | Açıklama            |
| ----------- | ------------- | ------------------- |
| `GET`       | `/`           | Ana sayfa           |
| `GET`       | `/tasks`      | Görevleri listeleme |
| `POST`      | `/tasks`      | Yeni görev ekleme   |
| `PUT`       | `/tasks/<id>` | Görev güncelleme    |
| `DELETE`    | `/tasks/<id>` | Görev silme         |

### 15.3. Bilerek eklenecek problemler

Demo amacıyla uygulamada kontrollü biçimde aşağıdaki problemler bulunabilir:

* TODO yorumu
* Uzun fonksiyon
* Boş except bloğu
* Yanlış isimlendirilmiş sınıf
* Hardcoded demo secret
* Gerçek güvenlik açığı verisiyle eşleşen bağımlılık

Bilerek eklenen problemlerin yalnızca eğitim ve demo amacı taşıdığı README içerisinde açıklanacaktır.

Gerçek bir parola, API anahtarı veya erişim anahtarı kullanılmayacaktır.

## 16. Raporlama Tasarımı

### 16.1. Terminal raporu

Terminal raporu kısa ve okunabilir olacaktır.

Örnek:

```text
[HIGH] SEC001 sample_app/app.py:14
Possible hardcoded password detected.
Recommendation: Read the value from an environment variable.
```

### 16.2. JSON raporu

Örnek:

```json
{
  "tool": "static-analyzer",
  "target": "sample_app",
  "summary": {
    "total": 1,
    "high": 1
  },
  "findings": [
    {
      "rule_id": "SEC001",
      "rule_name": "hardcoded-secret",
      "file_path": "sample_app/app.py",
      "line_number": 14,
      "severity": "high",
      "message": "Possible hardcoded password detected.",
      "recommendation": "Read the value from an environment variable."
    }
  ]
}
```

## 17. Hata Yönetimi

Aşağıdaki hatalar özel olarak ele alınacaktır:

* Kaynak klasörünün bulunamaması
* Requirements dosyasının bulunamaması
* Dosya izin hatası
* Dosya karakter kodlama hatası
* Python syntax hatası
* Geçersiz CLI parametresi
* JSON raporunun yazılamaması
* OSV API bağlantı hatası
* OSV API timeout hatası
* Geçersiz paket sürümü
* Desteklenmeyen requirements satırı

Tek bir dosyadaki hata mümkünse tüm taramayı durdurmamalıdır.

Kullanıcıya teknik traceback yerine öncelikle anlaşılır hata mesajı gösterilmelidir.

Geliştirme sırasında traceback bilgisi debug seçeneğiyle gösterilebilir.

## 18. Güvenlik Kararları

### 18.1. Secret değerlerinin maskelenmesi

Hardcoded secret tespit edildiğinde bulunan değerin tamamı raporda gösterilmeyecektir.

Örneğin:

```text
Detected possible hardcoded secret assigned to variable 'password'.
```

Değerin kendisi rapora yazılmayacaktır.

### 18.2. Gerçek secret kullanılmaması

Örnek uygulamada gerçek erişim anahtarı, parola veya bağlantı bilgisi kullanılmayacaktır.

Yalnızca açıkça sahte olduğu belli olan demo değerleri kullanılacaktır.

### 18.3. Harici API zaman aşımı

OSV API isteklerinde timeout kullanılacaktır.

Bu sayede servis cevap vermediğinde pipeline sonsuza kadar beklemeyecektir.

### 18.4. Bağımlılık doğrulaması

Projeye eklenecek paketlerin gerçekten var olduğu ve güvenilir kaynaktan geldiği kontrol edilecektir.

AI tarafından önerilen paket isimleri doğrulanmadan kurulmayacaktır.

## 19. Test Stratejisi

### 19.1. Unit testler

Her kural bağımsız olarak test edilecektir.

Her kural için en az:

* Bir pozitif test
* Bir negatif test
* Uygunsa bir sınır testi

Örnek:

```text
29 satırlık fonksiyon → bulgu yok
30 satırlık fonksiyon → yapılandırmaya göre bulgu yok
31 satırlık fonksiyon → bulgu var
```

### 19.2. Scanner testleri

Aşağıdaki durumlar test edilecektir:

* Tek Python dosyası
* İç içe klasörler
* Boş klasör
* Hariç tutulan klasör
* Syntax hatalı dosya
* Okunamayan dosya

### 19.3. Parser testleri

Aşağıdaki requirements satırları test edilecektir:

```text
requests==2.31.0
Flask==3.0.0
# comment

invalid-package-line
```

### 19.4. OSV istemci testleri

Unit testlerde gerçek API çağrısı yapılmayacaktır.

Mock veya yerel fixture kullanılacaktır.

Test edilecek durumlar:

* Güvenlik açığı bulunması
* Güvenlik açığı bulunmaması
* Boş API cevabı
* Timeout
* HTTP hatası
* Geçersiz JSON cevabı

### 19.5. Entegrasyon testleri

* Statik analiz aracının örnek uygulamada çalıştırılması
* Bağımlılık tarayıcının örnek requirements dosyasında çalıştırılması
* JSON raporlarının oluşturulması
* Exit code sonuçlarının kontrol edilmesi

## 20. GitHub Actions Pipeline Tasarımı

Pipeline Pull Request ve `main` branch’e push sırasında çalışacaktır.

Önerilen sıra:

1. Repository kodunu checkout et
2. Python kur
3. Bağımlılıkları yükle
4. Unit testleri çalıştır
5. Statik analiz aracını kendi kodunda çalıştır
6. Statik analiz aracını örnek uygulamada çalıştır
7. Bağımlılık tarayıcıyı çalıştır
8. JSON raporlarını oluştur
9. Belirlenen eşiklerde pipeline sonucunu belirle

Örnek akış:

```text
Pull Request
     |
     v
Checkout
     |
     v
Python Setup
     |
     v
Install Dependencies
     |
     v
Run Tests
     |
     v
Run Static Analyzer
     |
     v
Run Dependency Scanner
     |
     v
Pass or Fail
```

## 21. Pipeline Eşik Tasarımı

Araç kaynak kodu ve bilerek problemli örnek uygulama aynı eşikle analiz edilmemelidir.

Önerilen yaklaşım:

### Araç kaynak kodu

```text
HIGH veya CRITICAL bulguda pipeline başarısız
```

### Örnek uygulama

```text
Bulgular raporlanır ancak demo problemleri nedeniyle doğrudan pipeline başarısız olmayabilir
```

Örnek uygulama için beklenen bulgu sayıları entegrasyon testlerinde kontrol edilebilir.

Bu tasarım, bilerek problemli uygulamanın pipeline'ı sürekli başarısız hale getirmesini engeller.

## 22. Genişletilebilirlik

Yeni statik analiz kuralları aşağıdaki adımlarla eklenebilecektir:

1. `rules` klasöründe yeni bir kural dosyası oluşturulur.
2. Kural `BaseRule` arayüzünü uygular.
3. Kural aktif kural listesine eklenir.
4. Pozitif ve negatif testler yazılır.
5. Dokümantasyona kural açıklaması eklenir.

Yeni rapor formatları reporter katmanına eklenebilir.

Yeni advisory kaynakları ortak bir provider arayüzü üzerinden sisteme dahil edilebilir.

## 23. Teknik Kararlar ve Alternatifler

### Karar 1 — Tek büyük dosya yerine modüler yapı

Seçilen:

```text
Her bileşen ve kural için ayrı modül
```

Neden:

* Test edilebilirlik
* Okunabilirlik
* Genişletilebilirlik
* Review kolaylığı

### Karar 2 — Her şey için regex kullanılmaması

Seçilen:

```text
Metinsel problemler için regex, yapısal problemler için AST
```

Neden:

* Regex Python söz dizimini tam olarak anlayamaz.
* AST yorum satırlarını saklamadığı için TODO kontrolünde yeterli değildir.
* Her problem için en uygun yöntem farklıdır.

### Karar 3 — Canlı API ile test yapılmaması

Seçilen:

```text
Normal kullanımda OSV, testlerde yerel fixture
```

Neden:

* Testlerin kararlı olması
* İnternet bağımlılığının azaltılması
* API hızının test sonuçlarını etkilememesi

### Karar 4 — Basit web uygulaması

Seçilen:

```text
Flask ve in-memory veri
```

Neden:

* Projenin ana amacı web geliştirme değildir.
* Veritabanı kullanmak kapsamı gereksiz büyütebilir.
* Analiz araçlarını göstermek için basit bir hedef yeterlidir.

## 24. Bilinen Sınırlamalar

İlk sürümde aşağıdaki sınırlamalar bulunacaktır:

* Yalnızca Python dosyaları analiz edilecektir.
* Gelişmiş veri akışı analizi yapılmayacaktır.
* Bazı kurallar false positive üretebilir.
* İlk requirements parser tüm bağımlılık formatlarını desteklemeyebilir.
* OSV her kayıtta doğrudan önem seviyesi vermeyebilir.
* OSV her güvenlik kaydında güvenli sürüm bilgisini aynı biçimde sunmayabilir.
* İnternet bağlantısı yoksa canlı CVE sorgusu yapılamayabilir.
* Büyük projeler için özel performans optimizasyonu yapılmayacaktır.

## 25. Definition of Done

Bir özellik aşağıdaki koşullar sağlandığında tamamlanmış kabul edilecektir:

* Kod yazılmıştır.
* Kod geliştirici tarafından açıklanabilmektedir.
* Pozitif ve negatif testleri bulunmaktadır.
* Testler başarılıdır.
* Hata senaryoları ele alınmıştır.
* Gerekli dokümantasyon güncellenmiştir.
* Statik analiz aracı ilgili kod üzerinde çalıştırılmıştır.
* Pull Request açıklaması hazırlanmıştır.
* AI kullanılan bölümler PR açıklamasında belirtilmiştir.
* Review yorumları çözülmüştür.
