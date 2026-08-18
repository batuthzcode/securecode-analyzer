# Sample Web Application - Analysis

## Amaç

Bu bileşenin amacı, Static Code Analyzer ve Dependency Scanner bileşenlerinin üzerinde çalıştırılabileceği basit bir Flask web uygulaması geliştirmektir.

Uygulama, temel CRUD işlemlerini içerecek ve analiz araçlarının test edilebilmesi için kontrollü örnekler barındıracaktır.

## Kullanıcı İşlemleri

Kullanıcı aşağıdaki işlemleri yapabilecektir:

* Görevleri listeleme
* Yeni görev ekleme
* Mevcut görevi güncelleme
* Görev silme

## Veri Yapısı

Her görev için aşağıdaki bilgiler tutulacaktır:

* Görev kimliği
* Görev başlığı
* Görev açıklaması
* Tamamlanma durumu

İlk sürümde veriler uygulama çalıştığı sürece bellekte tutulacaktır.

Uygulama kapatıldığında verilerin silinmesi bu örnek proje için kabul edilmektedir.

## Sayfalar ve İşlemler

### Görev Listesi

Kayıtlı görevler kullanıcıya liste hâlinde gösterilecektir.

### Görev Ekleme

Kullanıcı form üzerinden yeni bir görev oluşturabilecektir.

### Görev Güncelleme

Kullanıcı mevcut bir görevin başlığını, açıklamasını veya tamamlanma durumunu değiştirebilecektir.

### Görev Silme

Kullanıcı seçilen görevi listeden kaldırabilecektir.

## Analiz Araçlarıyla İlişkisi

Uygulama, geliştirilen iki güvenlik bileşeninin test edilmesinde kullanılacaktır.

### Static Code Analyzer İçin

Uygulama içerisinde kontrollü olarak aşağıdaki örnekler bulunabilir:

* Uzun fonksiyon
* Boş `except` bloğu
* `TODO` veya `FIXME` ifadesi
* İsimlendirme problemi
* Örnek hardcoded secret

Bu örneklerin gerçek kullanıcı bilgisi veya gerçek anahtar içermemesi gerekir.

### Dependency Scanner İçin

Uygulamanın `requirements.txt` dosyasında test amacıyla belirlenmiş paket ve sürümler bulunacaktır.

Kullanılan örnek bağımlılığın gerçek advisory kaydıyla eşleşmesi gerekir.

## Girdi

* Web formundan girilen görev bilgileri
* URL üzerinden yapılan HTTP istekleri

## Çıktı

* Görev listesi
* Başarılı işlem mesajları
* Geçersiz girişler için hata mesajları
* Analiz araçlarının inceleyebileceği Python dosyaları
* Bağımlılık tarayıcısının inceleyebileceği `requirements.txt` dosyası

## Hata Durumları

Aşağıdaki durumlar kullanıcıya anlaşılır şekilde bildirilecektir:

* Boş görev başlığı girilmesi
* Bulunmayan görev kimliğiyle işlem yapılması
* Geçersiz form verisi gönderilmesi
* Güncelleme veya silme işleminin başarısız olması

## Güvenlik Sınırları

Bu uygulama üretim ortamı için hazırlanmayacaktır.

Aşağıdaki özellikler proje kapsamı dışındadır:

* Kullanıcı hesabı sistemi
* Gerçek veritabanı
* Yetkilendirme
* Ödeme sistemi
* Gerçek parola veya API anahtarı kullanımı

## Mevcut Durum

Temel Flask uygulaması, Task modeli, in-memory store ve JSON görev
listeleme/oluşturma/güncelleme/silme endpoint'leri tamamlanmıştır.

Sıradaki geliştirme adımları minimal frontend ve kontrollü analiz
örnekleridir.

## Flask Uygulama İskeleti Gereksinimleri

Bu aşama proje planındaki `Task 4.1.1` ve `Task 4.1.2` kapsamını
gerçekleştirecektir. CRUD endpoint'leri, HTML arayüzü ve bilerek problemli
analiz örnekleri sonraki aşamalarda eklenecektir.

### Paket ve Çalıştırma Yapısı

Uygulama, repository kökünde import edilebilir `sample_app` Python paketi
olarak bulunacaktır. Flask'ın uygulama factory yaklaşımı kullanılacak ve
paket aşağıdaki komutla çalıştırılabilecektir:

```powershell
flask --app sample_app run --debug
```

Factory fonksiyonu:

- `create_app()` adıyla paket arayüzünden erişilebilir olmalıdır.
- Test yapılandırmasını dışarıdan kabul etmelidir.
- Her çağrıda ayrı bir Flask uygulaması oluşturmalıdır.
- Global, uygulamalar arasında paylaşılan görev listesi oluşturmamalıdır.
- Testlerde özel bir in-memory store enjekte edilmesine izin vermelidir.

### İlk Ana Sayfa Sözleşmesi

Frontend eklenene kadar `GET /` endpoint'i JSON yanıtı döndürecektir.

Yanıt en az aşağıdaki alanları içermelidir:

```json
{
  "application": "SecureCode Analyzer Sample App",
  "tasks": []
}
```

`tasks` alanı o uygulama instance'ına ait store içindeki görevleri sıralı
olarak içermelidir. Endpoint yalnızca `GET` ve `HEAD` yöntemlerini kabul
etmelidir.

### Task Modeli

Her `Task` nesnesi aşağıdaki alanları taşımalıdır:

- `id`: Sıfırdan büyük, gerçek bir integer değer
- `title`: Kırpıldıktan sonra boş olmayan string
- `description`: Kırpılmış string; boş olabilir
- `completed`: Gerçek bir boolean değer

Model:

- Oluşturulduktan sonra değiştirilemez olmalıdır.
- Dinamik attribute eklenmesini engellemek için slot kullanmalıdır.
- JSON uyumlu dictionary çıktısı üretebilmelidir.
- Geçersiz değerleri kontrollü `ValueError` ile reddetmelidir.

### In-Memory Store

`InMemoryTaskStore` aşağıdaki davranışları sağlamalıdır:

- Başlangıç görevlerini ID sırasını koruyarak kabul etmelidir.
- Aynı ID'ye sahip iki başlangıç görevini reddetmelidir.
- Görevleri dışarıya immutable tuple olarak sunmalıdır.
- ID ile görev sorgulanmasına izin vermelidir.
- Yeni görevler için mevcut en büyük ID'den başlayan artan ID üretmelidir.
- Her uygulama factory çağrısında bağımsız olarak oluşturulmalıdır.

Uygulamanın ilk açılışında iki güvenli demo görevi bulunacaktır. Bu veriler
gerçek kullanıcı bilgisi, parola veya anahtar içermemelidir.

### Flask Bağımlılığı

Sample app çalışma gereksinimi tam sürüm sabitlemesiyle ayrı bir
`sample_app/requirements.txt` dosyasında tutulacaktır. Projenin geliştirme ve
sample-app optional dependency grupları Flask 3.1 serisini destekleyecektir.

### Kabul Kriterleri

1. `create_app()` test yapılandırmasıyla uygulama oluşturmalıdır.
2. `GET /` HTTP 200 ve beklenen JSON yapısını döndürmelidir.
3. İki ayrı factory çağrısı aynı mutable store'u paylaşmamalıdır.
4. Task modeli bütün alanlarını doğrulamalıdır.
5. Store duplicate ID değerini reddetmelidir.
6. Store yeni görevlerde deterministik ve artan ID üretmelidir.
7. Hedefli sample-app testleri ve mevcut tam test paketi geçmelidir.
8. Uygulama kaynakları compile kontrolünden geçmelidir.

## Görev Listeleme ve Oluşturma Gereksinimleri

Bu aşama proje planındaki `Task 4.2.1` ve `Task 4.2.2` kapsamını
gerçekleştirecektir. Görev güncelleme, silme ve HTML form yönlendirmeleri
sonraki aşamalarda eklenecektir.

### Görev Listeleme

```text
GET /tasks
```

Endpoint, uygulama instance'ına bağlı store içindeki görevleri insertion
order ile JSON olarak döndürmelidir.

Başarılı yanıt HTTP 200 olmalıdır:

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

Store boş olduğunda `tasks` alanı boş liste olmalıdır. Boş liste hata olarak
değerlendirilmemelidir.

### Görev Oluşturma

```text
POST /tasks
```

Endpoint aşağıdaki iki içerik türünü kabul etmelidir:

- `application/json`
- `application/x-www-form-urlencoded` veya `multipart/form-data`

Desteklenen alanlar:

- `title`: Zorunlu
- `description`: Opsiyonel, varsayılan boş string

Yeni görev her zaman `completed=false` olarak oluşturulmalıdır. İstemci `id`
veya `completed` değeri belirleyememelidir.

Başarılı oluşturma HTTP 201 ve aşağıdaki gövdeyi üretmelidir:

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

Oluşturulan görev aynı app instance'ındaki sonraki listeleme ve ana sayfa
yanıtlarında görünmelidir.

### İstek Doğrulaması

Aşağıdaki istekler reddedilmelidir:

- Desteklenmeyen content type
- Bozuk JSON
- JSON object yerine array, scalar veya `null`
- Eksik `title`
- String olmayan `title` veya `description`
- Kırpıldıktan sonra boş kalan `title`
- `title` ve `description` dışındaki alanlar

İstemci hataları JSON gövdesiyle döndürülmelidir:

```json
{
  "error": {
    "code": "invalid_task",
    "message": "title must not be empty."
  }
}
```

HTTP durumları:

- Geçersiz body veya alan: 400 Bad Request
- Desteklenmeyen content type: 415 Unsupported Media Type

Geçersiz oluşturma isteği store'u değiştirmemeli ve sonraki görev ID
değerini tüketmemelidir.

### Güvenlik Sınırları

- İstemciden gelen `id` kabul edilmez; ID yalnızca store tarafından üretilir.
- İstemciden gelen `completed` kabul edilmez; yeni görev incomplete başlar.
- Bilinmeyen alanlar sessizce saklanmaz veya modele aktarılmaz.
- Hata yanıtlarında traceback veya framework iç ayrıntısı bulunmaz.
- Endpoint authentication sağlamaz ve üretim API'si olarak sunulmaz.

### Kabul Kriterleri

1. `GET /tasks` dolu ve boş store sonuçlarını HTTP 200 ile döndürmelidir.
2. JSON ve form create istekleri HTTP 201 üretmelidir.
3. Başarılı create sonucu aynı store içinde listelenebilmelidir.
4. Başlık ve açıklama Task modeliyle normalize edilmelidir.
5. Bütün geçersiz body/alan durumları tutarlı JSON hata üretmelidir.
6. Unsupported media type HTTP 415 olmalıdır.
7. Geçersiz istek store veya ID sırasını değiştirmemelidir.
8. Mevcut ana sayfa ve factory izolasyonu korunmalıdır.
9. Hedefli ve tam test paketi geçmelidir.

## Görev Güncelleme ve Silme Gereksinimleri

Bu aşama proje planındaki `Task 4.2.3` ve `Task 4.2.4` kapsamını
gerçekleştirecektir. HTML edit sayfası ve form redirect davranışı minimal
frontend aşamasında eklenecektir.

### Görev Güncelleme

```text
PUT /tasks/<task_id>
```

Endpoint var olan görevin aşağıdaki alanlarından bir veya daha fazlasını
güncellemelidir:

- `title`
- `description`
- `completed`

Update kısmi alan değişikliğine izin verir. Payload içinde bulunmayan alanlar
mevcut değerlerini korur. `id` hiçbir zaman değiştirilemez.

JSON örneği:

```json
{
  "title": "Review final report",
  "completed": true
}
```

Başarılı yanıt HTTP 200 olmalıdır:

```json
{
  "task": {
    "id": 1,
    "title": "Review final report",
    "description": "Inspect the latest static analysis findings.",
    "completed": true
  }
}
```

Update işlemi immutable `Task` modelini yerinde değiştirmemeli; aynı ID ile
yeni bir Task değeri üretip store kaydını değiştirmelidir. Görevin insertion
order değeri korunmalıdır.

### Update İçerik Türleri

Create endpoint'iyle aynı içerik türleri desteklenmelidir:

- `application/json`
- `application/x-www-form-urlencoded`
- `multipart/form-data`

JSON `completed` değeri yalnızca gerçek boolean kabul etmelidir.

Form `completed` değeri büyük-küçük harf duyarsız aşağıdaki tokenları kabul
etmelidir:

```text
true:  true, 1, on, yes
false: false, 0, off, no
```

Başka completed değeri HTTP 400 üretmelidir.

### Update Doğrulaması

Aşağıdaki durumlar HTTP 400 ve kontrollü JSON hata üretmelidir:

- Boş update object veya boş form
- Bilinmeyen alan
- `id` alanı
- String olmayan `title` veya `description`
- Kırpıldıktan sonra boş kalan `title`
- JSON içinde boolean olmayan `completed`
- Form içinde desteklenmeyen completed tokenı
- Bozuk veya object olmayan JSON

Geçersiz update mevcut Task nesnesini veya store sırasını değiştirmemelidir.

### Görev Silme

```text
DELETE /tasks/<task_id>
```

Var olan görev store'dan kaldırılmalı ve endpoint HTTP 204 No Content
döndürmelidir. Response body boş olmalıdır.

Silinen görev ID değeri yeniden kullanılmamalıdır. Sonraki create işlemi
store'un monotonic `_next_id` değerinden devam etmelidir.

### Bulunamayan Görev

Update veya delete sırasında ID store içinde yoksa HTTP 404 döndürülmelidir:

```json
{
  "error": {
    "code": "task_not_found",
    "message": "Task 99 was not found."
  }
}
```

Olmayan görevin update/delete işlemi store'u değiştirmemelidir.

### Güvenlik Sınırları

- Path ID yalnızca pozitif integer route değeri olmalıdır.
- Update payload içindeki `id` ve bilinmeyen alanlar reddedilmelidir.
- Boolean değerler truthy/falsy genel Python dönüşümüyle çevrilmemelidir.
- Delete body içeriğine ihtiyaç duymamalıdır.
- Hata yanıtları traceback veya internal store ayrıntısı içermemelidir.
- Store process-local kalmalı; concurrency ve persistence bu aşamanın
  kapsamına girmemelidir.

### Kabul Kriterleri

1. PUT title, description ve completed alanlarını ayrı veya birlikte
   güncelleyebilmelidir.
2. Eksik update alanları mevcut değerini korumalıdır.
3. Update yeni immutable Task üretmeli ve insertion order'ı korumalıdır.
4. JSON ve form boolean sözleşmeleri doğrulanmalıdır.
5. Boş ve geçersiz update payload değerleri HTTP 400 üretmelidir.
6. Olmayan task update/delete işlemleri HTTP 404 JSON döndürmelidir.
7. Başarılı delete HTTP 204 ve boş body döndürmelidir.
8. Silinen ID yeniden kullanılmamalıdır.
9. Geçersiz update/delete store state değerini değiştirmemelidir.
10. Hedefli ve tam test paketi geçmelidir.

## Navigation

- [Sample Web Application sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
