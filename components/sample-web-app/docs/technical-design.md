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

Planlanan temel klasör yapısı aşağıdaki gibidir:

```text
sample-web-app/
├── app.py
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

* Flask uygulamasının oluşturulması
* CRUD rotalarının geliştirilmesi
* HTML şablonlarının hazırlanması
* Form kontrollerinin eklenmesi
* Kontrollü analiz örneklerinin eklenmesi
* `requirements.txt` test dosyasının hazırlanması
* Temel uygulama testlerinin yazılması

## Navigation

- [Sample Web Application sayfasına dön](../README.md)
- [Tüm bileşenlere dön](../../README.md)
- [Projenin ana sayfasına dön](../../../README.md)