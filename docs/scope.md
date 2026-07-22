# İş Tanımı ve Kapsam Dokümanı

## 1. Projenin Amacı

Bu projenin amacı, Python projelerinde temel kod kalitesi problemlerini tespit eden bir statik kod analiz aracı ve kullanılan bağımlılıklardaki bilinen güvenlik açıklarını tespit eden bir bağımlılık güvenlik tarama aracı geliştirmektir.

Geliştirilecek araçlar komut satırı üzerinden çalışabilecek, terminal veya JSON formatında rapor oluşturabilecek ve CI/CD süreçlerine entegre edilebilecektir.

## 2. Çözülecek Problem

Yazılım projelerinde kod kalitesi problemleri ve güvenlik açığı bulunan bağımlılıklar manuel incelemelerde gözden kaçabilir.

Bu proje aşağıdaki problemlere temel seviyede çözüm üretmeyi hedeflemektedir:

- Çok uzun fonksiyonların tespit edilmesi
- Boş `except` bloklarının bulunması
- TODO ve FIXME ifadelerinin raporlanması
- İsimlendirme kurallarına uymayan sınıf ve fonksiyonların belirlenmesi
- Kod içerisine sabit olarak yazılmış olabilecek parola ve erişim anahtarlarının tespit edilmesi
- Güvenlik açığı bulunan Python bağımlılıklarının belirlenmesi
- Kontrollerin CI/CD sürecinde otomatik olarak çalıştırılması

## 3. Proje Kapsamı

Proje kapsamında aşağıdaki bileşenler geliştirilecektir:

- Python kaynak dosyalarını tarayan statik analiz aracı
- En az 3-5 statik analiz kuralı
- `requirements.txt` dosyasını okuyabilen bağımlılık tarayıcı
- Gerçek kaynaklardan alınmış güvenlik açığı verileriyle karşılaştırma
- Terminal çıktısı
- JSON raporu
- Önem seviyesine göre exit code üretimi
- Basit örnek web uygulaması
- Unit ve entegrasyon testleri
- GitHub Actions CI/CD pipeline
- Kurulum ve kullanım dokümantasyonu

## 4. Kapsam Dışı Konular

Aşağıdaki konular ilk sürümün kapsamı dışında tutulacaktır:

- Python dışındaki programlama dillerinin analizi
- SonarQube seviyesinde gelişmiş statik analiz
- Trivy seviyesinde kapsamlı bağımlılık ve container taraması
- Veri akışı ve kontrol akışı analizi
- Üretim ortamına hazır büyük bir web uygulaması
- Gerçek zamanlı güvenlik takip paneli
- Kullanıcı hesabı ve yetkilendirme sistemi
- Otomatik kod düzeltme
- Tüm Python bağımlılık formatlarının desteklenmesi

## 5. Hedef Kullanıcılar

Projenin hedef kullanıcıları şunlardır:

- Python geliştiricileri
- Yazılım geliştirme ekipleri
- DevOps ekipleri
- Temel güvenlik kontrolleri yapmak isteyen öğrenciler
- CI/CD süreçlerine kalite ve güvenlik kontrolü eklemek isteyen ekipler

## 6. Kullanım Senaryoları

### Statik kod analizi

Kullanıcı analiz edilecek Python proje klasörünü komut satırından araca verir. Araç Python dosyalarını tarar, aktif kuralları çalıştırır ve tespit edilen problemleri raporlar.

### Bağımlılık taraması

Kullanıcı bir `requirements.txt` dosyasını araca verir. Araç bağımlılık isimlerini ve sürümlerini okur, güvenlik açığı verileriyle karşılaştırır ve bulunan açıkları raporlar.

### CI/CD kullanımı

Araçlar bir Pull Request sırasında GitHub Actions üzerinden çalıştırılır. Belirlenen önem seviyesinin üzerinde bir problem bulunursa pipeline başarısız olur.

## 7. Başarı Kriterleri

Proje aşağıdaki koşullar sağlandığında başarılı kabul edilecektir:

- Statik analiz aracı Python dosyalarını tarayabilmelidir.
- En az üç statik analiz kuralı doğru şekilde çalışmalıdır.
- Bulgularda dosya adı ve satır numarası bulunmalıdır.
- Terminal ve JSON çıktısı üretilebilmelidir.
- `requirements.txt` dosyasındaki bağımlılıklar okunabilmelidir.
- En az bir gerçek güvenlik açığı doğru şekilde tespit edilebilmelidir.
- CVE ve advisory verileri gerçek güvenilir kaynaklardan alınmalıdır.
- Araçlar analiz sonucuna göre exit code üretmelidir.
- Temel bileşenler unit testlerle doğrulanmalıdır.
- Araçlar GitHub Actions içerisinde çalıştırılabilmelidir.
- Kurulum ve kullanım adımları README dosyasında açıklanmalıdır.

## Navigation

- [Proje dokümantasyonuna dön](README.md)
- [Tüm bileşenlere git](../components/README.md)
- [Projenin ana sayfasına dön](../README.md)