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

Sıradaki geliştirmeler:

* CRUD rotalarının geliştirilmesi
* HTML şablonlarının hazırlanması
* Form kontrollerinin eklenmesi
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
- Ana sayfa route'unu kaydeder.
- Uygulama instance'ına bağlı store'u güvenli şekilde çözer.

`sample_app/models.py`:

- Immutable ve doğrulanan `Task` veri modelini içerir.
- JSON uyumlu `to_dict()` dönüşümünü sağlar.

`sample_app/store.py`:

- In-memory görev koleksiyonunu yönetir.
- Sıralı listeleme ve ID ile sorgulama sağlar.
- Artan görev kimliği üretir.
- Başlangıç demo verisini oluşturur.

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

## Navigation

- [Sample Web Application sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
