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

Bu bileşen şu anda analiz ve teknik tasarım aşamasındadır.

Geliştirme sırasında önce temel Flask uygulaması, ardından CRUD işlemleri ve analiz örnekleri eklenecektir.

## Navigation

- [Sample Web Application sayfasına dön](../README.md)
- [Tüm bileşenlere dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)