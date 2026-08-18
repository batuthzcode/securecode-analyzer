# Sample Web Application

## Amaç

Statik kod analiz aracı ve bağımlılık güvenlik tarayıcısının test edileceği basit bir Flask web uygulaması geliştirmek.

## Planlanan Özellikler

* Görevleri listeleme
* Yeni görev ekleme
* Mevcut görevi güncelleme
* Görev silme
* Basit HTML arayüzü
* Verileri uygulama çalıştığı sürece bellekte tutma
* Statik analiz aracının tespit edebileceği kontrollü örnekler içerme
* Bağımlılık tarayıcısının test edilebileceği örnek `requirements.txt` dosyası içerme

## Kullanılacak Yöntemler

* Web uygulaması için Flask
* Arayüz için HTML
* Verileri geçici olarak saklamak için Python listesi veya sözlüğü

## Girdi

Kullanıcı tarafından web arayüzünden girilen görev bilgileri.

## Çıktı

* Görev listesi
* Ekleme, güncelleme ve silme işlemlerinin sonuçları
* Analiz araçları tarafından incelenebilecek örnek proje yapısı

## Documentation

- [Analiz ve Gereksinimler](analysis.md)
- [Teknik Tasarım](technical-design.md)

## Mevcut Durum

Flask application foundation tamamlanmıştır.

Mevcut özellikler:

* Test edilebilir `create_app()` application factory
* Immutable ve doğrulanan `Task` modeli
* Uygulama instance'ına özel `InMemoryTaskStore`
* Güvenli ve deterministik başlangıç demo verisi
* Geçici JSON ana sayfa endpoint'i
* Flask test client ile model, store ve HTTP testleri

CRUD endpoint'leri, HTML/CSS arayüzü ve bilerek problemli güvenlik analiz
örnekleri sonraki aşamalarda eklenecektir.

## Kurulum

Sample app bağımlılığını proje virtual environment'ına kurmak için:

```powershell
python -m pip install -e ".[sample-app]"
```

Test bağımlılıklarını da kurmak için:

```powershell
python -m pip install -e ".[dev]"
```

Sample uygulamanın doğrudan ve sabitlenmiş çalışma bağımlılığı:

```text
sample_app/requirements.txt
```

Bu dosya güncel Flask 3.1 sürümünü sabitler:

```text
Flask==3.1.3
```

Flask yalnızca analyzer araçlarını kullanan kurulumların zorunlu ana
bağımlılığı değildir.

## Çalıştırma

Repository kökünde:

```powershell
flask --app sample_app run --debug
```

Uygulama varsayılan olarak aşağıdaki adreste çalışır:

```text
http://127.0.0.1:5000
```

Flask geliştirme sunucusu yalnızca yerel geliştirme ve demo amacıyla
kullanılmalıdır.

## İlk HTTP Sözleşmesi

Frontend aşamasına kadar ana sayfa görevleri JSON olarak döndürür:

```text
GET /
```

Örnek yanıt:

```json
{
  "application": "SecureCode Analyzer Sample App",
  "tasks": [
    {
      "id": 1,
      "title": "Review analyzer report",
      "description": "Inspect the latest static analysis findings.",
      "completed": false
    },
    {
      "id": 2,
      "title": "Prepare security demo",
      "description": "Verify the dependency scan example.",
      "completed": true
    }
  ]
}
```

Ana endpoint salt okunurdur. `POST /` gibi desteklenmeyen yöntemler HTTP 405
üretir.

## Foundation Mimarisi

```text
sample_app/__init__.py
  -> public package interface

sample_app/app.py
  -> create_app()
  -> Flask route registration
  -> app.extensions store binding

sample_app/models.py
  -> immutable Task model
  -> validation and JSON conversion

sample_app/store.py
  -> ordered in-memory storage
  -> ID lookup and generation
  -> deterministic demo tasks
```

Module-level mutable görev listesi kullanılmaz. Her `create_app()` çağrısı
ayrı bir store üretir; testler gerektiğinde kendi store instance'ını factory
fonksiyonuna enjekte eder.

## Task Modeli

Görev alanları:

| Alan | Tür | Kural |
|---|---|---|
| `id` | `int` | Sıfırdan büyük olmalıdır. |
| `title` | `str` | Kırpıldıktan sonra boş olamaz. |
| `description` | `str` | Kırpılır, boş olabilir. |
| `completed` | `bool` | Yalnızca gerçek boolean kabul edilir. |

`Task` modeli frozen dataclass ve slot kullanır. CRUD güncelleme aşamasında
var olan model yerinde değiştirilmeyecek, yeni değer store'a yazılacaktır.

## Store Davranışı

`InMemoryTaskStore`:

* Görev sırasını korur.
* Immutable tuple snapshot döndürür.
* Duplicate başlangıç ID değerini reddeder.
* ID ile görev sorgular.
* En büyük başlangıç ID değerinden sonra artan ID üretir.
* Yeni görevleri varsayılan olarak tamamlanmamış oluşturur.

Veriler yalnızca process belleğinde bulunur ve uygulama kapandığında silinir.

## Testler

Hedefli testler:

```powershell
pytest tests/test_sample_app_models.py `
  tests/test_sample_app_store.py `
  tests/test_sample_app.py -q
```

Doğrulama sonucu:

```text
Sample app foundation: 40 passed
Complete test suite: 868 passed
Compile check: passed
Sample app self-analysis: no findings
Analyzer source self-analysis: no findings
```

Testler Flask geliştirme sunucusunu veya gerçek ağ bağlantısını başlatmaz.
HTTP davranışı Flask test client ile process içinde doğrulanır.

## Resmî Kaynaklar

Foundation tasarımı Flask'ın resmî application factory ve test client
yaklaşımını kullanır:

* [Flask Application Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
* [Testing Flask Applications](https://flask.palletsprojects.com/en/stable/testing/)
* [Flask 3.1.3 on PyPI](https://pypi.org/project/Flask/3.1.3/)

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
