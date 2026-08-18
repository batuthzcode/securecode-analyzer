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

Flask CRUD uygulaması, minimal frontend, kontrollü güvenlik fixture'ları ve
yeniden üretilebilir entegrasyon raporları tamamlanmıştır.

Mevcut özellikler:

* Test edilebilir `create_app()` application factory
* Immutable ve doğrulanan `Task` modeli
* Uygulama instance'ına özel `InMemoryTaskStore`
* Güvenli ve deterministik başlangıç demo verisi
* Jinja ile render edilen HTML görev çalışma alanı
* JSON görev listeleme endpoint'i
* JSON ve form verisiyle görev oluşturma endpoint'i
* JSON ve form verisiyle kısmi görev güncelleme endpoint'i
* Görev silme endpoint'i
* Kontrollü JSON doğrulama hataları
* Browser create/edit/delete formları ve `303` yönlendirmeleri
* Responsive, erişilebilir temel CSS
* Flask test client ile model, store, API ve frontend testleri
* Beş deterministik static analyzer bulgusu
* Ayrı ve runtime dışı vulnerable dependency fixture'ı
* Portable static-analysis ve dependency-scan JSON baseline'ları
* Offline report generator ve drift check
* Pull Request ve `main` push için test, static ve dependency CI job'ları

Sıradaki aşama security report artifact upload job'udur.

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

Vulnerable dependency fixture normal uygulama kurulumu için kullanılmamalıdır:

```text
sample_app/requirements-vulnerable.txt
```

Bu dosya yalnızca dependency scanner demosunun girdisidir.

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

## Web Arayüzü

Ana sayfa görev çalışma alanını HTML olarak gösterir:

```text
GET /
```

Arayüz aşağıdaki özellikleri içerir:

* Toplam, pending ve completed görev sayaçları
* Görev oluşturma formu
* Durum bilgisiyle sıralı görev kartları
* Görev düzenleme sayfası
* POST tabanlı görev silme formu
* Boş store ve kontrollü form hata görünümleri
* Dar ekranlara uyumlu layout ve görünür klavye focus durumları

Ana endpoint salt okunurdur. `POST /` gibi desteklenmeyen yöntemler HTTP 405
üretir.

Tarayıcı create, edit ve delete formları başarılı işlemden sonra HTTP 303 ile
ana sayfaya yönlendirilir. JSON API aynı rotalarda mevcut response
sözleşmesini korur.

Browser form rotaları:

```text
POST     /tasks
GET/POST /tasks/<id>/edit
POST     /tasks/<id>/delete
```

## Görev Listeleme API'si

```text
GET /tasks
```

Yanıt, store içindeki görevleri oluşturulma sırasıyla döndürür:

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Review analyzer report",
      "description": "Inspect the latest static analysis findings.",
      "completed": false
    }
  ]
}
```

Boş store için HTTP 200 ve `{"tasks": []}` döner.

## Görev Oluşturma API'si

```text
POST /tasks
```

JSON örneği:

```powershell
$body = @{
    title = "Prepare release notes"
    description = "Summarize analyzer changes."
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:5000/tasks `
    -ContentType application/json `
    -Body $body
```

Form örneği:

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:5000/tasks `
    -ContentType application/x-www-form-urlencoded `
    -Body @{
        title = "Prepare release notes"
        description = "Summarize analyzer changes."
    }
```

Başarılı istek HTTP 201 döndürür:

```json
{
  "task": {
    "id": 3,
    "title": "Prepare release notes",
    "description": "Summarize analyzer changes.",
    "completed": false
  }
}
```

Create endpoint'inde yalnızca `title` ve `description` kabul edilir. `id` ve
`completed` store tarafından yönetilir ve istemciden alınmaz.

## API Hataları

Geçersiz alan ve body hataları HTTP 400, desteklenmeyen content type HTTP 415
üretir. Bütün beklenen create hataları JSON olarak döner:

```json
{
  "error": {
    "code": "invalid_task",
    "message": "title must not be empty."
  }
}
```

Desteklenmeyen alanlar reddedilir; bozuk JSON veya object olmayan JSON body
store'a aktarılmaz. Geçersiz istek görev listesini değiştirmez ve yeni görev
ID değerini tüketmez.

## Görev Güncelleme API'si

```text
PUT /tasks/<id>
```

Update isteği `title`, `description` ve `completed` alanlarından en az birini
içermelidir. Gönderilmeyen alanlar mevcut değerini korur.

JSON örneği:

```powershell
$body = @{
    title = "Prepare final release notes"
    completed = $true
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Put `
    -Uri http://127.0.0.1:5000/tasks/3 `
    -ContentType application/json `
    -Body $body
```

Form örneği:

```powershell
Invoke-RestMethod `
    -Method Put `
    -Uri http://127.0.0.1:5000/tasks/3 `
    -ContentType application/x-www-form-urlencoded `
    -Body @{
        description = "Ready for review."
        completed = "yes"
    }
```

Başarılı update HTTP 200 ve güncel görevi döndürür. JSON `completed` alanı
yalnızca gerçek boolean kabul eder. Form verisinde `true`, `false`, `1`, `0`,
`on`, `off`, `yes` ve `no` değerleri büyük/küçük harf duyarsız olarak kabul
edilir. Boş payload, `null`, bilinmeyen alanlar ve geçersiz boolean değerleri
HTTP 400 üretir.

## Görev Silme API'si

```text
DELETE /tasks/<id>
```

PowerShell örneği:

```powershell
Invoke-WebRequest `
    -Method Delete `
    -Uri http://127.0.0.1:5000/tasks/3
```

Başarılı delete HTTP 204 ve boş body döndürür. Silinen görev listeden ve ana
sayfa yanıtından kaybolur. Silinen ID yeniden kullanılmaz.

## Bulunamayan Görev

Olmayan bir görev update veya delete edilmeye çalışıldığında HTTP 404 döner:

```json
{
  "error": {
    "code": "task_not_found",
    "message": "Task 99 was not found."
  }
}
```

## Kontrollü Static Analyzer Demo

Bilerek problemli örneklerin tamamı çalışan Flask kodundan ayrılmıştır:

```text
sample_app/analyzer_demo.py
```

Demo modülü application factory veya package interface tarafından import
edilmez. Analyzer komutu:

```powershell
securecode-analyzer sample_app --format text
```

Beklenen tam bulgu seti:

| Rule | Satır | Severity | Örnek |
|---|---:|---|---|
| `SA005` | 8 | warning | Açıkça sahte hardcoded secret |
| `SA001` | 11 | warning | 65 satırlık fonksiyon |
| `SA006` | 11 | info | camelCase fonksiyon adı |
| `SA003` | 14 | info | TODO comment |
| `SA004` | 54 | warning | Pass-only except handler |

Toplam tam olarak 5 finding beklenir. Secret finding raporu yalnızca genel
mesajı içerir; sahte literal değeri rapora yazılmaz.

## Vulnerable Dependency Demo

Scanner fixture değeri:

```text
fastapi==0.109.0
```

Canlı OSV taraması:

```powershell
securecode-dependency-scan `
  sample_app/requirements-vulnerable.txt `
  --source osv `
  --format json
```

Beklenen finding:

```text
advisory: PYSEC-2024-38
alias: CVE-2024-24762
severity: HIGH
fixed version: 0.109.1
```

FastAPI `0.109.0` normal `sample_app/requirements.txt` dosyasında bulunmaz,
kurulmaz ve Flask uygulaması tarafından import edilmez. Offline testler aynı
finding değerini checked-in OSV projection fixture'ıyla ağ kullanmadan
doğrular.

## Entegrasyon Raporları

Canonical JSON baseline'lar:

```text
reports/sample-app/static-analysis.json
reports/sample-app/dependency-scan.json
```

İki raporu production analyzer/scanner katmanlarından yeniden üretmek için:

```powershell
python tools/generate_sample_app_reports.py
```

Checked-in artifact'ların güncel olduğunu dosya yazmadan doğrulamak için:

```powershell
python tools/generate_sample_app_reports.py --check
```

Generator static analyzer'ı doğrudan çalıştırır. Dependency baseline için
checked-in, provenance bilgili OSV projection fixture'ını kullanır; bu nedenle
rapor üretimi internete veya zamanla değişen upstream response değerlerine
bağlı değildir. JSON içindeki dosya yolları Windows ve Linux üzerinde aynı
repository-relative `/` biçimindedir.

## Uçtan Uca Demo Sırası

1. Uygulamayı başlat:

   ```powershell
   flask --app sample_app run --debug
   ```

2. Ayrı terminalde kontrollü static analyzer finding'lerini göster:

   ```powershell
   securecode-analyzer sample_app --format text
   ```

   Beş finding nedeniyle exit code `1` beklenir.

3. Structured static baseline'ı aç:

   ```powershell
   Get-Content reports/sample-app/static-analysis.json
   ```

4. Vulnerable fixture için canlı OSV taramasını çalıştır:

   ```powershell
   securecode-dependency-scan `
     sample_app/requirements-vulnerable.txt `
     --source osv `
     --format json `
     --fail-on high
   ```

   HIGH finding nedeniyle exit code `1` beklenir.

5. Deterministik dependency baseline'ı ve drift kontrolünü göster:

   ```powershell
   Get-Content reports/sample-app/dependency-scan.json
   python tools/generate_sample_app_reports.py --check
   ```

Demo sonunda Flask runtime requirements dosyasının yalnızca `Flask==3.1.3`
içerdiği yeniden vurgulanmalıdır.

## Foundation Mimarisi

```text
sample_app/__init__.py
  -> public package interface

sample_app/app.py
  -> create_app()
  -> Flask route registration
  -> app.extensions store binding
  -> JSON API and browser form response mapping

sample_app/models.py
  -> immutable Task model
  -> validation and JSON conversion

sample_app/store.py
  -> ordered in-memory storage
  -> ID lookup and generation
  -> deterministic demo tasks

sample_app/task_requests.py
  -> JSON/form content type selection
  -> create/update field validation
  -> strict boolean parsing
  -> controlled request errors

sample_app/templates/
  -> shared layout, task workspace and edit form

sample_app/static/style.css
  -> responsive layout, controls and task status styling

sample_app/analyzer_demo.py
  -> isolated, intentional static analyzer findings

sample_app/requirements-vulnerable.txt
  -> demo-only vulnerable dependency scanner input

tools/generate_sample_app_reports.py
  -> deterministic report generation and drift check

reports/sample-app/
  -> portable static and dependency JSON baselines
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

`Task` modeli frozen dataclass ve slot kullanır. Update sırasında var olan
model yerinde değiştirilmez; doğrulanmış yeni değer store'a yazılır.

## Store Davranışı

`InMemoryTaskStore`:

* Görev sırasını korur.
* Immutable tuple snapshot döndürür.
* Duplicate başlangıç ID değerini reddeder.
* ID ile görev sorgular.
* En büyük başlangıç ID değerinden sonra artan ID üretir.
* Yeni görevleri varsayılan olarak tamamlanmamış oluşturur.
* Immutable model replacement ile kısmi güncelleme yapar.
* Görev siler ve silinen ID değerini yeniden kullanmaz.

Veriler yalnızca process belleğinde bulunur ve uygulama kapandığında silinir.

## Testler

Hedefli testler:

```powershell
pytest tests/test_sample_app_models.py `
  tests/test_sample_app_store.py `
  tests/test_sample_app.py `
  tests/test_sample_app_task_routes.py `
  tests/test_sample_app_update_delete_routes.py `
  tests/test_sample_app_frontend.py `
  tests/test_sample_app_security_demo.py `
  tests/test_sample_app_reports.py -q
```

Doğrulama sonucu:

```text
Task route tests: 27 passed
New update/delete test cases: 54 passed
New frontend test cases: 18 passed
New security demo test cases: 4 passed
New integration report test cases: 6 passed
New CI workflow test cases: 13 passed
New offline dependency CI test cases: 5 passed
New Python 3.11 compatibility test cases: 1 passed
Sample app targeted suite: 149 passed
Complete test suite: 996 passed
Compile check: passed
Sample app analysis: 5 expected findings
Analyzer source self-analysis: no findings
Checked-in report drift check: passed
```

Testler Flask geliştirme sunucusunu veya gerçek ağ bağlantısını başlatmaz.
HTTP davranışı Flask test client ile process içinde doğrulanır.

## Resmî Kaynaklar

Foundation tasarımı Flask'ın resmî application factory ve test client
yaklaşımını kullanır:

* [Flask Application Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
* [Testing Flask Applications](https://flask.palletsprojects.com/en/stable/testing/)
* [Flask Templates](https://flask.palletsprojects.com/en/stable/tutorial/templates/)
* [Flask Static Files](https://flask.palletsprojects.com/en/stable/tutorial/static/)
* [Flask 3.1.3 on PyPI](https://pypi.org/project/Flask/3.1.3/)
* [OSV PYSEC-2024-38](https://osv.dev/vulnerability/PYSEC-2024-38)
* [FastAPI 0.109.0 on PyPI](https://pypi.org/project/fastapi/0.109.0/)

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
