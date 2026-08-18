# Sample Web Application - Technical Design

## Genel Yaklaşım

Sample Web Application, Static Code Analyzer ve Dependency Scanner bileşenlerinin test edilmesi için geliştirilecek basit bir Flask uygulamasıdır.

Uygulama temel CRUD işlemlerini destekleyecek ve ilk sürümde verileri bellekte tutacaktır.

## Kullanılacak Teknolojiler

* Python
* Flask
* HTML
* Basit CSS
* Jinja template sistemi

İlk sürümde veritabanı kullanılmayacaktır.

## Klasör Yapısı

Temel klasör yapısı aşağıdaki gibidir:

```text
sample_app/
├── __init__.py
├── app.py
├── models.py
├── store.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── edit.html
└── static/
    └── style.css
```

## Uygulama Akışı

Uygulamanın temel çalışma sırası aşağıdaki şekilde olacaktır:

1. Flask uygulaması başlatılır.
2. Kullanıcı ana sayfaya gider.
3. Mevcut görevler listelenir.
4. Kullanıcı form üzerinden yeni görev ekleyebilir.
5. Kullanıcı mevcut bir görevi güncelleyebilir.
6. Kullanıcı bir görevi silebilir.
7. İşlem tamamlandıktan sonra kullanıcı görev listesine yönlendirilir.

## Veri Modeli

Her görev aşağıdaki alanları içerecektir:

```json
{
  "id": 1,
  "title": "Örnek görev",
  "description": "Görev açıklaması",
  "completed": false
}
```

Alanların anlamları:

* `id`: Görevi benzersiz olarak tanımlar.
* `title`: Görevin başlığıdır.
* `description`: Görevle ilgili açıklamadır.
* `completed`: Görevin tamamlanıp tamamlanmadığını belirtir.

## Veri Saklama

İlk sürümde görevler Python listesi içerisinde tutulacaktır.

Örnek:

```python
tasks = []
```

Uygulama kapatıldığında listedeki veriler silinecektir. Bu durum örnek uygulama kapsamında kabul edilmektedir.

## Planlanan Rotalar

### Ana Sayfa

```text
GET /
```

Görevlerin listesini ve görev ekleme formunu gösterir.

### Görev Ekleme

```text
POST /tasks
```

Formdan gelen bilgilerle yeni görev oluşturur.

### Görev Düzenleme Sayfası

```text
GET /tasks/<task_id>/edit
```

Seçilen görevin düzenleme formunu gösterir.

### Görev Güncelleme

```text
POST /tasks/<task_id>/edit
```

Seçilen görevin bilgilerini günceller.

### Görev Silme

```text
POST /tasks/<task_id>/delete
```

Seçilen görevi listeden kaldırır.

## Şablonlar

HTML sayfaları Flask ile birlikte kullanılan Jinja template sistemiyle oluşturulacaktır.

Planlanan şablonlar:

* `index.html`: Görev listesini ve ekleme formunu gösterir.
* `edit.html`: Mevcut görevin düzenlenmesini sağlar.

## Girdi Kontrolü

Kullanıcıdan gelen bilgiler kullanılmadan önce kontrol edilecektir.

Özellikle aşağıdaki durumlar kontrol edilecektir:

* Görev başlığının boş olması
* Görev kimliğinin bulunamaması
* Geçersiz form verisi gönderilmesi
* Beklenmeyen HTTP yöntemi kullanılması

## Hata Yönetimi

Görev bulunamadığında uygulamanın kontrolsüz şekilde hata vermesi engellenecektir.

Kullanıcıya anlaşılır bir hata mesajı gösterilecek veya görev listesine yönlendirme yapılacaktır.

## Static Analyzer Testleri

Uygulama içerisinde analiz aracının tespit edebileceği kontrollü örnekler bulunacaktır.

Örnekler:

* Belirlenen sınırdan uzun fonksiyon
* Boş `except` bloğu
* `TODO` veya `FIXME` ifadesi
* Python isimlendirme kurallarına uymayan isim
* Gerçek olmayan örnek secret değeri

Bu örnekler yalnızca analiz aracını test etmek amacıyla kullanılacaktır.

## Dependency Scanner Testleri

Uygulamanın `requirements.txt` dosyası Dependency Scanner tarafından analiz edilecektir.

Test için kullanılacak paket sürümü seçilirken gerçek bir advisory kaydıyla eşleşmesi kontrol edilecektir.

Gerçek projelerde kullanılmaması gereken eski veya güvensiz sürümler yalnızca kontrollü test amacıyla kullanılacaktır.

## Güvenlik Sınırları

Bu uygulama üretim ortamında kullanılmayacaktır.

Aşağıdaki özellikler kapsam dışındadır:

* Kullanıcı doğrulama sistemi
* Yetkilendirme sistemi
* Kalıcı veritabanı
* Gerçek kullanıcı bilgileri
* Gerçek parola veya API anahtarı
* Üretim ortamı dağıtımı

## Gelecek Geliştirmeler

Tamamlanan foundation çalışmaları:

* Flask application factory oluşturulması
* Immutable Task modelinin geliştirilmesi
* In-memory store ve demo verisinin eklenmesi
* JSON ana sayfa endpoint'inin eklenmesi
* Temel uygulama testlerinin yazılması
* JSON task create, list, partial update ve delete rotalarının eklenmesi
* JSON/form request doğrulaması ve kontrollü API hatalarının eklenmesi
* Jinja ana sayfa ve task edit template'lerinin eklenmesi
* Browser form redirect ve HTML hata akışlarının eklenmesi
* Responsive temel stylesheet'in eklenmesi

Sıradaki geliştirmeler:

* Kontrollü analiz örneklerinin eklenmesi
* Gerçek advisory için ayrı vulnerable requirements fixture'ının hazırlanması

## Flask Foundation Teknik Tasarımı

### Uygulama Factory

Paketin public giriş noktası aşağıdaki imzaya sahip olacaktır:

```python
def create_app(
    test_config: Mapping[str, object] | None = None,
    *,
    task_store: InMemoryTaskStore | None = None,
) -> Flask:
    ...
```

Factory:

1. Yeni bir `Flask` instance'ı oluşturur.
2. Varsa test yapılandırmasını uygular.
3. Enjekte edilen store'u veya demo verili yeni store'u seçer.
4. Store'u `app.extensions` içinde uygulama instance'ına bağlar.
5. Route kayıtlarını gerçekleştirir.
6. Hazır Flask uygulamasını döndürür.

Store'un `app.extensions` altında tutulması module-level mutable state
oluşmasını engeller. Böylece testler ve aynı process içindeki farklı uygulama
instance'ları birbirinden izole kalır.

### Modül Sorumlulukları

`sample_app/__init__.py`:

- Public `create_app`, model ve store arayüzünü dışa aktarır.

`sample_app/app.py`:

- Flask factory fonksiyonunu içerir.
- Ana sayfa ve task route'larını kaydeder.
- Uygulama instance'ına bağlı store'u güvenli şekilde çözer.
- Domain sonuçlarını JSON response değerlerine dönüştürür.

`sample_app/models.py`:

- Immutable ve doğrulanan `Task` veri modelini içerir.
- JSON uyumlu `to_dict()` dönüşümünü sağlar.

`sample_app/store.py`:

- In-memory görev koleksiyonunu yönetir.
- Sıralı listeleme ve ID ile sorgulama sağlar.
- Artan görev kimliği üretir.
- Başlangıç demo verisini oluşturur.

`sample_app/task_requests.py`:

- JSON ve form content type seçimini yapar.
- Create ve update request alanlarını doğrular.
- JSON ve form boolean değerlerini açık bir sözleşmeyle ayrıştırır.
- Beklenen istemci hatalarını kontrollü modele dönüştürür.

### İlk Route

Frontend geliştirilene kadar ana route aşağıdaki geçici JSON sözleşmesini
kullanır:

```text
GET /
```

Başarılı yanıt:

```json
{
  "application": "SecureCode Analyzer Sample App",
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

Flask JSON provider response serialization işlemini üstlenir. Route doğrudan
store'un mutable iç yapısını döndürmez; her görevin `to_dict()` sonucunu yeni
bir listede üretir.

### Veri Modeli ve Store Sınırları

`Task`, `dataclass(frozen=True, slots=True)` olarak uygulanır. Güncelleme
aşamasında var olan instance değiştirilmez; yeni bir Task değeri oluşturulup
store içindeki kayıt değiştirilir.

Store görevleri insertion order koruyan dictionary içinde saklar. Python
dictionary sırası deterministik listeleme sağlar. `_next_id` değeri başlangıç
görevlerindeki en büyük ID artı bir olarak hesaplanır.

Store public yöntemleri:

```text
list_tasks() -> tuple[Task, ...]
get_task(task_id: int) -> Task | None
create_task(title: str, description: str = "") -> Task
```

Update ve delete store yöntemleri CRUD aşamasında eklenecektir.

### Bağımlılık Politikası

`sample_app/requirements.txt`, uygulamanın doğrudan çalıştırma bağımlılığını
tam sürümle sabitler. Root `pyproject.toml` içinde:

- `sample-app` extra grubu sample uygulamayı çalıştırmak için kullanılır.
- `dev` extra grubu test paketinin Flask testlerini çalıştırabilmesini sağlar.

Flask yalnızca analyzer CLI araçlarını kullanan kurulumlar için zorunlu ana
bağımlılık yapılmaz.

### Test Stratejisi

Unit testler:

- Task normalizasyonu ve serialization
- Geçersiz ID, title, description ve completed değerleri
- Model immutability ve slot kullanımı
- Boş ve başlangıç verili store davranışı
- Duplicate ID koruması
- Sıralı listeleme ve artan ID üretimi

Flask test client testleri:

- Factory yapılandırması
- Store injection
- Ana sayfa JSON sözleşmesi
- Uygulama instance izolasyonu
- Desteklenmeyen HTTP yöntemi için 405 sonucu

Flask geliştirme sunucusu test sırasında açılmaz; bütün HTTP kontrolleri
Flask test client ile process içinde çalışır.

## Task List ve Create Teknik Tasarımı

### Route Kaydı

Uygulama factory aşağıdaki iki route'u aynı app instance'ına kaydeder:

```text
GET  /tasks -> list_tasks()
POST /tasks -> create_task()
```

Route fonksiyonları module-level mutable veri kullanmaz. Her istek store'u
mevcut application context içindeki `app.extensions` kaydından çözer.

### Listeleme Akışı

```text
GET /tasks
  -> current app store
  -> list_tasks()
  -> Task.to_dict()
  -> {"tasks": [...]}
  -> HTTP 200
```

Response için yeni dictionary/list değerleri üretilir. Store'un internal
dictionary değeri veya mutable view nesnesi istemciye aktarılmaz.

### Oluşturma Akışı

```text
POST /tasks
  -> content type selection
  -> JSON or form payload
  -> allowed field validation
  -> title/description type validation
  -> InMemoryTaskStore.create_task()
  -> Task.to_dict()
  -> {"task": {...}}
  -> HTTP 201
```

Request parser HTTP payload sözleşmesini doğrular. Task modeli domain
doğrulamasını ve whitespace normalizasyonunu yapmaya devam eder.

### Content Type Seçimi

JSON istekleri Flask `request.is_json` ve `request.get_json(silent=True)`
ile okunur. `silent=True`, bozuk JSON için framework HTML hata sayfası yerine
uygulamanın kontrollü JSON hata sözleşmesini üretmesini sağlar.

Form isteklerinde yalnızca aşağıdaki mimetype değerleri desteklenir:

```text
application/x-www-form-urlencoded
multipart/form-data
```

Başka content type değerleri payload parse edilmeden HTTP 415 ile
reddedilir.

### Request Veri Modeli

Parse edilen geçerli değer aşağıdaki internal veri modeline dönüştürülür:

```python
@dataclass(frozen=True, slots=True)
class CreateTaskRequest:
    title: str
    description: str = ""
```

Bu model HTTP request ile Task domain modeli arasındaki sınırı açık tutar.
`id` ve `completed` alanları create request modelinde bulunmaz.

### Hata Modeli

Request parser beklenen istemci hataları için kontrollü bir
`TaskRequestError` üretir. Hata aşağıdaki bilgileri taşır:

```text
code
message
status_code
```

Route bu hatayı aşağıdaki JSON biçimine dönüştürür:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Request body must contain a valid JSON object."
  }
}
```

Task modelinden gelen beklenen `ValueError` değerleri `invalid_task` ve HTTP
400 olarak eşlenir. Beklenmeyen exception değerleri yakalanmaz; test modunda
gizlenmeden yükselir.

### Alan Politikası

Allowed field kümesi:

```text
title
description
```

Payload içinde başka bir alan bulunduğunda alan adları sıralanarak hata
mesajına eklenir. Bu yaklaşım testleri deterministik tutar ve mass-assignment
benzeri istem dışı alan aktarımını engeller.

### Test Stratejisi

HTTP entegrasyon testleri en az aşağıdaki durumları kapsar:

- Dolu görev listesi
- Boş görev listesi
- Insertion order korunması
- JSON ile görev oluşturma
- Form ile görev oluşturma
- Opsiyonel description varsayılanı
- Text alanlarının normalizasyonu
- Oluşturulan görevin `/tasks` ve `/` yanıtında görünmesi
- Eksik ve geçersiz title
- Geçersiz description
- Bozuk ve object olmayan JSON
- Desteklenmeyen content type
- Bilinmeyen alanlar
- Geçersiz isteğin store ve ID sırasını değiştirmemesi

Testler resmî Flask test client `json=` ve `data=` parametrelerini kullanır;
gerçek HTTP sunucusu veya ağ bağlantısı başlatılmaz.

## Task Update ve Delete Teknik Tasarımı

### Route Kaydı

```text
PUT    /tasks/<int:task_id> -> update_task(task_id)
DELETE /tasks/<int:task_id> -> delete_task(task_id)
```

Flask `int` converter path değerini integer olarak view fonksiyonuna aktarır.
Store doğrulaması pozitif ID sözleşmesini korumaya devam eder.

### Store Update

Store public update yöntemi:

```python
def update_task(
    task_id: int,
    *,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
) -> Task | None:
    ...
```

Akış:

```text
validate task_id
  -> find current Task
  -> return None when missing
  -> select provided or current field values
  -> construct a new validated Task
  -> replace dictionary value for the same key
  -> return updated Task
```

Var olan dictionary key'e yeni değer atanması insertion order'ı değiştirmez.
Yeni Task başarıyla oluşturulmadan store'a atama yapılmaz; validation hatası
state değerini korur.

### Store Delete

Store public delete yöntemi:

```python
def delete_task(task_id: int) -> Task | None:
    ...
```

Yöntem kaldırılan Task değerini, bulunamayan ID için `None` döndürür.
`_next_id` delete sırasında değiştirilmez; böylece silinen kimlikler yeniden
kullanılmaz.

### Update Request Modeli

```python
@dataclass(frozen=True, slots=True)
class UpdateTaskRequest:
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

Parser explicit `null` değerlerini reddettiği için `None` yalnızca alanın
payload içinde bulunmadığını ve mevcut değerin korunacağını ifade eder.

### Boolean Parsing

JSON payload için:

```text
true  -> True
false -> False
```

String, integer ve null JSON değerleri reddedilir.

Form payload için normalize edilmiş token tabloları kullanılır:

```text
{"true", "1", "on", "yes"}   -> True
{"false", "0", "off", "no"} -> False
```

Genel `bool(value)` dönüşümü kullanılmaz; örneğin `bool("false")` değerinin
yanlışlıkla `True` üretmesi engellenir.

### Update Route Akışı

```text
positive task_id
  -> current task lookup
  -> 404 when missing
  -> parse_update_task_request()
  -> store.update_task()
  -> {"task": updated.to_dict()}
  -> HTTP 200
```

Task modelinden gelen `ValueError`, create endpoint'iyle aynı
`invalid_task` HTTP 400 JSON yanıtına dönüştürülür.

### Delete Route Akışı

```text
positive task_id
  -> store.delete_task()
  -> 404 when missing
  -> empty Flask Response
  -> HTTP 204
```

DELETE route request body parse etmez.

### Not Found Hatası

Update ve delete aynı helper üzerinden aşağıdaki hatayı üretir:

```json
{
  "error": {
    "code": "task_not_found",
    "message": "Task 99 was not found."
  }
}
```

Bu hata HTTP 404 durum kodunu taşır.

### Test Stratejisi

Store unit testleri:

- Tek alan ve çoklu alan update
- Immutable eski snapshot'ın değişmemesi
- Update sırasında insertion order korunması
- Missing task update/delete
- Validation hatasında state korunması
- Başarılı delete
- Delete sonrasında ID yeniden kullanılmaması

HTTP entegrasyon testleri:

- JSON ve form PUT
- Title, description ve completed partial update
- JSON boolean strict validation
- Bütün desteklenen form boolean tokenları
- Boş payload ve bilinmeyen alanlar
- Geçersiz text alanları
- Missing task için update/delete 404
- Başarılı delete 204 ve boş body
- Delete sonucunun ana sayfa ve listede görünmesi
- Silinen ID sonrasında monotonic create
- Update/delete için desteklenmeyen HTTP yöntemleri

## Minimal Frontend Teknik Tasarımı

### Render ve Static Yapısı

```text
sample_app/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── edit.html
└── static/
    └── style.css
```

Flask package template ve static klasörlerini varsayılan konumlarından
yükler. Template URL değerleri hardcode edilmez; `url_for()` ile üretilir.
Jinja `.html` template autoescape davranışı kullanıcı title ve description
değerlerini HTML injection'a karşı sınırlar.

### Ana Sayfa View Modeli

`_render_index()` helper değeri template'e aşağıdaki alanları aktarır:

```text
application_name
tasks
task_counts.total
task_counts.completed
task_counts.pending
error
form_values.title
form_values.description
```

Task nesneleri template'e doğrudan aktarılır. JSON serialization yalnızca API
response helper içinde kullanılır.

### İçerik Tercihi

Create endpoint'i JSON ve form API uyumluluğunu korur. HTML response yalnızca
istemcinin `Accept` başlığında `text/html` kalitesi `application/json`
kalitesinden yüksek olduğunda seçilir. Böylece:

```text
browser form + Accept: text/html -> HTML error veya redirect
JSON request                     -> JSON response
form request + no Accept         -> JSON response
```

Wildcard `Accept: */*` JSON davranışını korur.

### Post/Redirect/Get

Başarılı browser write akışları:

```text
POST form
  -> shared request parser
  -> in-memory store mutation
  -> redirect(url_for("index"), code=303)
  -> GET /
```

Create `POST /tasks` rotasını kullanır. Edit ve delete için HTML-only adapter
rotaları eklenir:

```text
GET  /tasks/<int:task_id>/edit   -> edit form
POST /tasks/<int:task_id>/edit   -> update + 303
POST /tasks/<int:task_id>/delete -> delete + 303
```

JSON API rotaları aynı store yöntemlerini kullanmaya devam eder:

```text
GET    /tasks
POST   /tasks
PUT    /tasks/<int:task_id>
DELETE /tasks/<int:task_id>
```

### Edit Formu

Edit form title, description ve completed alanlarını her zaman gönderir.
Completed alanı `true` ve `false` değerlerini sunan select kontrolüdür; unchecked
checkbox alanının request'ten tamamen kaybolması gibi belirsiz bir durum
oluşturmaz. Form payload mevcut strict update parser üzerinden doğrulanır.

### HTML Hata Akışı

Create doğrulama hatası ana sayfayı, edit doğrulama hatası edit sayfasını
yeniden render eder. Her ikisi de HTTP 400 değerini korur ve kullanıcı text
alanlarını Jinja autoescape altında forma geri yazar.

Olmayan edit/delete görevi `_render_index()` ile HTTP 404 üretir. API
update/delete rotalarının mevcut JSON `task_not_found` sözleşmesi değişmez.

### Stil ve Erişilebilirlik

Tek stylesheet aşağıdaki davranışları sağlar:

- Dar ekranlarda tek kolon, geniş ekranda dengeli form/list layout
- Görünür label, focus ring ve button/link state değerleri
- Text ile desteklenen completed/pending status badge değerleri
- Description için güvenli line wrapping
- Empty state ve hata banner'ı
- Harici font, script veya görsel olmadan sistem fontları

### Frontend Test Stratejisi

- HTML content type ve temel landmark/form içeriği
- Dolu ve boş store render davranışı
- Kullanıcı title/description değerlerinin autoescape edilmesi
- Static stylesheet endpoint'i
- Browser create redirect ve inline validation error
- Edit form prefill, başarılı redirect ve invalid state koruması
- Delete redirect, missing task 404 ve GET ile delete edilememe
- Form action/link URL değerleri
- Mevcut JSON API regresyon paketi

## Navigation

- [Sample Web Application sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
