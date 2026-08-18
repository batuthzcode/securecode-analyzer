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

Temel Flask uygulaması, Task modeli ve in-memory store tamamlanmıştır.

Sıradaki geliştirme adımları CRUD işlemleri, minimal frontend ve kontrollü
analiz örnekleridir.

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

## Navigation

- [Sample Web Application sayfasına dön](README.md)
- [Tüm bileşenlere dön](../README.md)
- [Proje dokümantasyonuna dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)
