# Proje Planı

## 1. Dokümanın Amacı

Bu dokümanın amacı, Python tabanlı statik kod analiz aracı, bağımlılık ve CVE tarama aracı, örnek web uygulaması ve CI/CD entegrasyonu için beş haftalık çalışma planını tanımlamaktır.

Plan içerisinde işler backlog, task ve sub-task seviyesinde ayrılmıştır. Ayrıca işlerin öncelikleri, bağımlılıkları, riskleri, minimum tamamlanabilir proje kapsamı ve zaman kalması durumunda yapılabilecek opsiyonel geliştirmeler açıklanmıştır.

## 2. Proje Süresi

Planlanan çalışma dönemi:

```text
20 Temmuz – 21 Ağustos
```

Toplam süre:

```text
5 hafta
```

Çalışma sırası:

1. Analiz ve planlama
2. Statik kod analiz aracı
3. Bağımlılık ve CVE tarama aracı
4. Örnek web uygulaması ve entegrasyon
5. CI/CD, test, dokümantasyon ve sunum

## 3. Öncelik Seviyeleri

İşlerin öncelikleri aşağıdaki şekilde değerlendirilecektir:

| Öncelik | Açıklama                                       |
| ------- | ---------------------------------------------- |
| P0      | Projenin çalışması için zorunlu                |
| P1      | Minimum tamamlanabilir proje kapsamında önemli |
| P2      | Zaman kalırsa yapılması faydalı                |
| P3      | Opsiyonel geliştirme                           |

## 4. İş Durumları

Backlog içerisinde aşağıdaki durumlar kullanılacaktır:

| Durum       | Açıklama                                          |
| ----------- | ------------------------------------------------- |
| Backlog     | Henüz başlanmamış                                 |
| To Do       | Yakında başlanacak                                |
| In Progress | Üzerinde çalışılıyor                              |
| Review      | Pull Request açılmış ve inceleme bekliyor         |
| Done        | Test edilmiş, onaylanmış ve merge edilmiş         |
| Blocked     | Başka bir iş veya problem nedeniyle ilerleyemiyor |

## 5. Definition of Done

Bir task aşağıdaki şartlar sağlandığında tamamlanmış kabul edilir:

* Kod veya doküman hazırlanmıştır.
* Değişiklik ayrı bir branch üzerinde yapılmıştır.
* Anlaşılır commit mesajları yazılmıştır.
* Gerekli testler hazırlanmıştır.
* Testler başarıyla çalışmaktadır.
* Hata senaryoları kontrol edilmiştir.
* İlgili dokümanlar güncellenmiştir.
* Pull Request açılmıştır.
* PR açıklamasında yapılan değişiklikler ve testler belirtilmiştir.
* AI kullanılan bölümler açıklanmıştır.
* Review yorumları çözülmüştür.
* Değişiklik ana branch’e merge edilmiştir.

# 6. Hafta 1 — Analiz ve Planlama

## Haftalık hedef

Projenin kapsamını doğru anlamak, teknik kararları belgelemek, repository yapısını hazırlamak ve çalışan küçük bir AST prototipi geliştirmek.

## Backlog 1.1 — Repository kurulumu

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Yok

### Task 1.1.1 — GitHub repository oluşturma

Sub-task’ler:

* Public GitHub repository oluştur.
* Repository adını belirle.
* Ana branch adını `main` olarak ayarla.
* Repository’yi GitHub Desktop ile bilgisayara klonla.
* İlk README dosyasını oluştur.
* İlk commit’i yap.
* Repository’yi GitHub’a gönder.

### Task 1.1.2 — Branch çalışma düzeni

Sub-task’ler:

* `docs/initial-analysis` branch’ini oluştur.
* Geliştirmelerin doğrudan `main` üzerinde yapılmaması kuralını belirle.
* Branch isimlendirme yaklaşımını dokümante et.

Önerilen branch isimleri:

```text
docs/initial-analysis
feature/static-analyzer-core
feature/static-analysis-rules
feature/dependency-scanner
feature/sample-application
ci/github-actions
docs/final-documentation
```

### Task 1.1.3 — Başlangıç dosyaları

Sub-task’ler:

* `.gitignore` oluştur.
* `requirements-dev.txt` oluştur.
* Proje klasör yapısını belirle.
* `docs` klasörünü oluştur.
* Sanal ortam klasörünün repoya eklenmediğini kontrol et.

## Backlog 1.2 — Kapsam analizi

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Repository kurulumu

### Task 1.2.1 — Kapsam özeti

Sub-task’ler:

* Projenin amacını kendi cümlelerinle yaz.
* Çözülecek problemi açıkla.
* Proje kapsamını belirle.
* Kapsam dışı konuları belirle.
* Hedef kullanıcıları tanımla.
* Kullanım senaryolarını yaz.
* Başarı kriterlerini oluştur.

Çıktı:

```text
docs/scope.md
```

## Backlog 1.3 — Gereksinim analizi

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Kapsam analizi

### Task 1.3.1 — Fonksiyonel gereksinimler

Sub-task’ler:

* Kaynak klasörü seçme gereksinimini yaz.
* Python dosyası tarama gereksinimini yaz.
* Statik analiz kurallarını tanımla.
* Terminal çıktısı gereksinimini yaz.
* JSON çıktısı gereksinimini yaz.
* Exit code gereksinimini yaz.
* Requirements parser gereksinimini yaz.
* CVE eşleştirme gereksinimini yaz.
* CI/CD çalışma gereksinimini yaz.

### Task 1.3.2 — Fonksiyonel olmayan gereksinimler

Sub-task’ler:

* Kullanılacak Python sürümünü belirle.
* Modülerlik beklentisini yaz.
* Test edilebilirlik beklentisini yaz.
* Hata toleransını tanımla.
* Güvenlik verisi doğruluğu kuralını yaz.
* Secret bilgilerinin korunmasını tanımla.
* Windows ve Linux uyumluluğunu yaz.
* Dokümantasyon gereksinimini yaz.

### Task 1.3.3 — Hata senaryoları

Sub-task’ler:

* Kaynak klasörü bulunamadığında davranışı belirle.
* Syntax hatalı dosya davranışını belirle.
* Requirements dosyası bulunamadığında davranışı belirle.
* Hatalı paket satırı davranışını belirle.
* OSV servisi çalışmadığında davranışı belirle.
* Rapor dosyası yazılamadığında davranışı belirle.

### Task 1.3.4 — Kabul kriterleri

Sub-task’ler:

* Her fonksiyonel gereksinim için test edilebilir kabul kriteri yaz.
* Statik analiz kuralları için pozitif ve negatif kabul kriterleri oluştur.
* CVE tarama sonuçları için doğruluk kriteri oluştur.
* Pipeline başarı ve başarısızlık koşullarını tanımla.

Çıktı:

```text
docs/analysis.md
```

## Backlog 1.4 — Teknik tasarım

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Gereksinim analizi

### Task 1.4.1 — Sistem mimarisi

Sub-task’ler:

* Ana bileşenleri belirle.
* CLI katmanını tanımla.
* Statik analiz katmanını tanımla.
* Bağımlılık tarama katmanını tanımla.
* Raporlama katmanını tanımla.
* Pipeline akışını tanımla.

### Task 1.4.2 — Regex ve AST kararları

Sub-task’ler:

* TODO/FIXME için regex yaklaşımını açıkla.
* Uzun fonksiyon için AST yaklaşımını açıkla.
* Boş except için AST yaklaşımını açıkla.
* İsimlendirme için AST ve regex birlikte kullanımını açıkla.
* Hardcoded secret için AST ve regex birlikte kullanımını açıkla.
* Her yaklaşımın avantaj ve risklerini yaz.

### Task 1.4.3 — Modül tasarımı

Sub-task’ler:

* Statik analiz modüllerini belirle.
* Bağımlılık tarayıcı modüllerini belirle.
* Model sınıflarını belirle.
* Reporter sorumluluklarını belirle.
* Kural arayüzünü belirle.
* OSV istemcisinin sorumluluklarını belirle.

### Task 1.4.4 — CLI tasarımı

Sub-task’ler:

* Statik analiz komutunu tasarla.
* Bağımlılık tarama komutunu tasarla.
* Parametreleri belirle.
* Exit code değerlerini belirle.
* Yardım mesajı yaklaşımını tanımla.

### Task 1.4.5 — Test stratejisi

Sub-task’ler:

* Unit test yaklaşımını belirle.
* Entegrasyon testlerini belirle.
* API testlerinde mock kullanımını belirle.
* Geçici dosya ve klasör testlerini planla.
* CI ortamında çalışacak testleri belirle.

Çıktı:

```text
docs/technical-design.md
```

## Backlog 1.5 — İlk AST prototipi

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Temel teknik tasarım

### Task 1.5.1 — Örnek Python dosyası

Sub-task’ler:

* Bilerek uzun bir fonksiyon içeren Python dosyası oluştur.
* Dosyayı `examples` klasörüne ekle.
* Fonksiyonun başlangıç ve bitiş satırlarını belirle.

### Task 1.5.2 — AST ile parse işlemi

Sub-task’ler:

* Dosyayı `pathlib` ile oku.
* Kaynak kodu `ast.parse()` ile parse et.
* Parse hatasını yakala.
* AST ağacındaki fonksiyonları bul.

### Task 1.5.3 — İlk kural

Sub-task’ler:

* Fonksiyon başlangıç satırını al.
* Fonksiyon bitiş satırını al.
* Fonksiyon uzunluğunu hesapla.
* Belirlenen sınır aşılırsa terminal çıktısı üret.
* Dosya ve satır numarasını raporla.

### Task 1.5.4 — Prototip testi

Sub-task’ler:

* Uzun fonksiyon için bulgu oluştuğunu kontrol et.
* Kısa fonksiyon için bulgu oluşmadığını kontrol et.
* Syntax hatalı dosya durumunu kontrol et.

## Hafta 1 teslimleri

* `scope.md`
* `analysis.md`
* `technical-design.md`
* `project-plan.md`
* Başlangıç klasör yapısı
* İlk AST prototipi
* İlk Pull Request
* Haftalık rapor

# 7. Hafta 2 — Statik Kod Analiz Aracı

## Haftalık hedef

Python dosyalarını tarayan, en az üç ila beş temel kural çalıştıran, terminal ve JSON çıktısı üreten test edilmiş bir statik analiz aracı geliştirmek.

## Backlog 2.1 — Çekirdek veri modelleri

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Teknik tasarım

### Task 2.1.1 — Severity modeli

Sub-task’ler:

* Önem seviyelerini enum olarak tanımla.
* Seviyelerin sıralamasını belirle.
* `fail-on` karşılaştırmasında kullanılacak mekanizmayı oluştur.

Önem seviyeleri:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

### Task 2.1.2 — Finding modeli

Sub-task’ler:

* Kural kimliğini ekle.
* Kural adını ekle.
* Dosya yolunu ekle.
* Satır numarasını ekle.
* Önem seviyesini ekle.
* Problem mesajını ekle.
* Çözüm önerisini ekle.
* Dictionary dönüşüm metodu ekle.

## Backlog 2.2 — Kural altyapısı

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Finding modeli

### Task 2.2.1 — BaseRule oluşturma

Sub-task’ler:

* Soyut temel sınıf oluştur.
* Kural kimliği alanını tanımla.
* Kural adı alanını tanımla.
* Önem seviyesi alanını tanımla.
* `analyze` metodunu tanımla.

### Task 2.2.2 — Kural kayıt mekanizması

Sub-task’ler:

* Aktif kurallar listesini oluştur.
* Scanner’ın kuralları sırayla çalıştırmasını sağla.
* Yeni kural eklemenin kolay olmasını sağla.

## Backlog 2.3 — Dosya tarayıcı

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Kural altyapısı

### Task 2.3.1 — Python dosyalarını bulma

Sub-task’ler:

* Kullanıcıdan hedef dizini al.
* Hedef dizinin varlığını kontrol et.
* Alt klasörleri dolaş.
* `.py` dosyalarını bul.

### Task 2.3.2 — Hariç tutulan klasörler

Sub-task’ler:

* `.git` klasörünü atla.
* `.venv` klasörünü atla.
* `venv` klasörünü atla.
* `__pycache__` klasörünü atla.
* `.pytest_cache` klasörünü atla.

### Task 2.3.3 — Dosya okuma

Sub-task’ler:

* UTF-8 kodlamasıyla dosya oku.
* Dosya izin hatasını yakala.
* Karakter kodlama hatasını yakala.
* Bir dosyadaki hata nedeniyle tüm taramayı durdurma.

### Task 2.3.4 — AST oluşturma

Sub-task’ler:

* Kaynak kodu bir kez parse et.
* AST gerektiren kurallara aynı ağacı gönder.
* Syntax hatasını bulgu veya hata olarak raporla.

## Backlog 2.4 — Statik analiz kuralları

**Öncelik:** P0
**Tahmini süre:** 2 gün
**Bağımlılık:** Scanner ve kural altyapısı

### Task 2.4.1 — TODO/FIXME kuralı

Sub-task’ler:

* Dosyayı satır satır oku.
* TODO kelimesini bul.
* FIXME kelimesini bul.
* Dosya ve satır numarası oluştur.
* String içinde geçen ifadelerin false positive riskini değerlendir.
* Pozitif ve negatif test yaz.

### Task 2.4.2 — Uzun fonksiyon kuralı

Sub-task’ler:

* `FunctionDef` düğümlerini bul.
* `AsyncFunctionDef` düğümlerini bul.
* Başlangıç ve bitiş satırını hesapla.
* Varsayılan eşik belirle.
* Eşik dışarıdan değiştirilebilir olsun.
* Sınır testi yaz.

### Task 2.4.3 — Boş except kuralı

Sub-task’ler:

* `ExceptHandler` düğümlerini bul.
* Body yalnızca `pass` içeriyorsa raporla.
* Çıplak except durumunu ayrıca değerlendir.
* Yorum içeren ama yalnızca pass bulunan bloğu test et.
* Pozitif ve negatif test yaz.

### Task 2.4.4 — İsimlendirme kuralı

Sub-task’ler:

* Fonksiyon isimlerini AST ile bul.
* Fonksiyon adını `snake_case` regex ile kontrol et.
* Sınıf isimlerini AST ile bul.
* Sınıf adını `PascalCase` regex ile kontrol et.
* Dunder metotları yanlışlıkla raporlamamayı değerlendir.
* Testleri yaz.

### Task 2.4.5 — Hardcoded secret kuralı

Sub-task’ler:

* Şüpheli değişken isimleri listesini oluştur.
* Atama düğümlerini AST ile bul.
* Değerin sabit string olup olmadığını kontrol et.
* `os.getenv()` kullanımını temiz kabul et.
* Secret değerini rapora yazma.
* False positive örnekleri test et.

## Backlog 2.5 — Raporlama

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Finding modeli

### Task 2.5.1 — Terminal raporu

Sub-task’ler:

* Önem seviyesini göster.
* Kural adını göster.
* Dosya ve satır numarasını göster.
* Problem açıklamasını göster.
* Çözüm önerisini göster.
* Toplam bulgu sayısını göster.

### Task 2.5.2 — JSON raporu

Sub-task’ler:

* Araç adını ekle.
* Hedef dizini ekle.
* Özet alanını ekle.
* Bulgular listesini ekle.
* UTF-8 JSON dosyası oluştur.
* Çıktı klasörü yoksa oluşturmayı değerlendir.

## Backlog 2.6 — CLI

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Scanner ve reporter

### Task 2.6.1 — Argparse kurulumu

Sub-task’ler:

* Hedef dizin parametresi ekle.
* `--format` parametresi ekle.
* `--output` parametresi ekle.
* `--fail-on` parametresi ekle.
* `--exclude` parametresi ekle.
* `--max-function-lines` parametresi ekle.

### Task 2.6.2 — Exit code

Sub-task’ler:

* Bulguları önem seviyesine göre kontrol et.
* Eşik üzerindeki bulguda `1` döndür.
* Kullanıcı hatasında `2` döndür.
* Beklenmeyen hatada `3` döndür.
* Başarılı durumda `0` döndür.

## Backlog 2.7 — Testler ve PR

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Statik analiz aracının tamamlanması

### Task 2.7.1 — Unit testler

Sub-task’ler:

* Her kural için pozitif test yaz.
* Her kural için negatif test yaz.
* Eşik sınır testlerini yaz.
* Syntax hatalı dosya testini yaz.
* Hariç tutulan klasör testini yaz.
* JSON çıktı testini yaz.
* Exit code testini yaz.

### Task 2.7.2 — Kendi kodunu analiz etme

Sub-task’ler:

* Aracı `static_analyzer` klasöründe çalıştır.
* Aracı `dependency_scanner` klasörü hazırsa orada çalıştır.
* Bulunan gerçek problemleri düzelt.
* False positive sonuçları not et.

### Task 2.7.3 — Pull Request

Sub-task’ler:

* Feature branch oluştur.
* Küçük ve anlaşılır commit’ler oluştur.
* Test komutlarını PR açıklamasına ekle.
* AI kullanılan bölümleri belirt.
* Review yorumlarını düzelt.

## Hafta 2 teslimleri

* Çalışan statik analiz CLI
* En az üç temel kural
* Tercihen beş kural
* Terminal çıktısı
* JSON raporu
* Exit code sistemi
* Unit testler
* Pull Request
* Haftalık rapor

# 8. Hafta 3 — Bağımlılık ve CVE Tarama Aracı

## Haftalık hedef

`requirements.txt` dosyasını okuyabilen, paket ve sürüm bilgilerini gerçek güvenlik verileriyle karşılaştıran ve güvenlik bulgularını raporlayan çalışan bir PoC geliştirmek.

## Backlog 3.1 — Bağımlılık veri modeli

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Teknik tasarım

### Task 3.1.1 — Dependency modeli

Sub-task’ler:

* Paket adı alanı oluştur.
* Sürüm alanı oluştur.
* Orijinal requirements satırını saklamayı değerlendir.
* Paket adını normalize eden yapı oluştur.

### Task 3.1.2 — DependencyFinding modeli

Sub-task’ler:

* Paket adı alanı oluştur.
* Kullanılan sürüm alanı oluştur.
* Advisory kimliği alanı oluştur.
* CVE kimliklerini sakla.
* Açıklama alanı oluştur.
* Önem seviyesi alanı oluştur.
* Güvenli sürüm alanı oluştur.
* Kaynak bilgisi alanı oluştur.

## Backlog 3.2 — Requirements parser

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Dependency modeli

### Task 3.2.1 — Dosya okuma

Sub-task’ler:

* Requirements dosyasının varlığını kontrol et.
* Dosyayı UTF-8 ile oku.
* Boş satırları atla.
* Yorum satırlarını atla.

### Task 3.2.2 — Sabit sürüm formatı

Sub-task’ler:

* `package==version` formatını ayır.
* Paket adını temizle.
* Sürüm değerini temizle.
* Büyük ve küçük harf normalizasyonu yap.
* Tire ve alt çizgi normalizasyonunu değerlendir.

### Task 3.2.3 — Desteklenmeyen formatlar

Sub-task’ler:

* `>=` formatını tespit et.
* `~=` formatını tespit et.
* Git URL satırlarını tespit et.
* Editable kurulum satırlarını tespit et.
* Desteklenmeyen satırları kontrollü biçimde raporla.

## Backlog 3.3 — Gerçek güvenlik veri kaynağı

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Requirements parser

### Task 3.3.1 — OSV API araştırması

Sub-task’ler:

* OSV sorgu formatını incele.
* PyPI ecosystem değerini doğrula.
* Paket ve sürüm sorgusunu dene.
* API cevap yapısını incele.
* Hata durumlarını listele.

### Task 3.3.2 — OSV istemcisi

Sub-task’ler:

* HTTP isteği oluştur.
* Paket adı ve sürümü gönder.
* Timeout ekle.
* HTTP hata yönetimi ekle.
* Bağlantı hata yönetimi ekle.
* JSON cevabını ayrıştır.

### Task 3.3.3 — Yerel test verisi

Sub-task’ler:

* Gerçek bir OSV kaydı seç.
* Kaydın kaynağını belgeye ekle.
* Test için gerekli alanları JSON fixture olarak sakla.
* CVE veya advisory kimliğini değiştirme.
* Etkilenen sürüm bilgisini değiştirme.
* Güvenli sürüm bilgisini değiştirme.
* AI tarafından veri üretilmediğini doğrula.

## Backlog 3.4 — Sürüm ve advisory eşleştirme

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** OSV istemcisi

### Task 3.4.1 — Paket sürümü doğrulama

Sub-task’ler:

* `packaging.version.Version` kullan.
* Geçersiz sürüm değerini yakala.
* String karşılaştırması kullanma.
* Pre-release sürümlerini test et.

### Task 3.4.2 — Etkilenen sürüm kontrolü

Sub-task’ler:

* OSV affected bilgilerini incele.
* Aralık başlangıcını kontrol et.
* Fixed sürüm event’ini kontrol et.
* Kullanılan sürümün aralıkta olup olmadığını belirle.
* Birden fazla affected aralığını destekle.

### Task 3.4.3 — Güvenli sürüm belirleme

Sub-task’ler:

* Fixed event bilgisini çıkar.
* Birden fazla fixed sürüm varsa uygun olanı belirle.
* Bilgi yoksa `unknown` veya `null` kullan.
* Güvenli sürüm uydurma.

## Backlog 3.5 — Raporlama ve CLI

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Advisory eşleştirme

### Task 3.5.1 — Terminal raporu

Sub-task’ler:

* Paket adını göster.
* Kullanılan sürümü göster.
* Advisory kimliğini göster.
* CVE kimliğini göster.
* Önem seviyesini göster.
* Güvenli sürümü göster.
* Kaynağı göster.

### Task 3.5.2 — JSON raporu

Sub-task’ler:

* Taranan dosya yolunu ekle.
* Toplam bağımlılık sayısını ekle.
* Güvenlik açığı bulunan bağımlılık sayısını ekle.
* Bulguları listele.
* Kaynak bilgisini ekle.

### Task 3.5.3 — CLI parametreleri

Sub-task’ler:

* Requirements dosya yolunu al.
* `--format` ekle.
* `--output` ekle.
* `--fail-on` ekle.
* `--source` ekle.
* `--timeout` ekle.

## Backlog 3.6 — Testler

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** CVE tarayıcının tamamlanması

### Task 3.6.1 — Parser testleri

Sub-task’ler:

* Geçerli sabit sürüm testini yaz.
* Boş satır testini yaz.
* Yorum satırı testini yaz.
* Desteklenmeyen format testini yaz.
* Hatalı satır testini yaz.

### Task 3.6.2 — OSV istemci testleri

Sub-task’ler:

* Güvenlik açığı bulunan cevap testi yaz.
* Boş cevap testi yaz.
* HTTP hata testi yaz.
* Timeout testi yaz.
* Geçersiz JSON testi yaz.
* Testlerde canlı API çağrısı yapma.

### Task 3.6.3 — Sürüm eşleştirme testleri

Sub-task’ler:

* Etkilenen sürüm testi yaz.
* Güvenli sürüm testi yaz.
* Aralık sınır testi yaz.
* Pre-release sürüm testi yaz.
* Fixed sürüm bulunmayan kayıt testi yaz.

### Task 3.6.4 — Entegrasyon testi

Sub-task’ler:

* Örnek requirements dosyası oluştur.
* En az bir gerçek advisory ile eşleşme sağla.
* JSON raporunu kontrol et.
* Exit code değerini kontrol et.

## Hafta 3 teslimleri

* Requirements parser
* OSV istemcisi
* Yerel gerçek advisory fixture
* Sürüm eşleştirme mekanizması
* Terminal ve JSON çıktısı
* Exit code sistemi
* Unit ve entegrasyon testleri
* Pull Request
* Haftalık rapor

# 9. Hafta 4 — Örnek Web Uygulaması ve Entegrasyon

## Haftalık hedef

Analiz araçlarının üzerinde çalıştırılabileceği basit bir Flask uygulaması geliştirmek ve her iki aracı uygulamaya karşı çalıştırmak.

## Backlog 4.1 — Uygulama iskeleti

**Öncelik:** P1
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Statik analiz ve bağımlılık tarama araçları

### Task 4.1.1 — Flask kurulumu

Sub-task’ler:

* Flask bağımlılığını ekle.
* `sample_app` klasörünü oluştur.
* `app.py` oluştur.
* Uygulamayı çalıştır.
* Ana sayfa endpoint’ini oluştur.

### Task 4.1.2 — Veri modeli

Sub-task’ler:

* Görev nesnesi yapısını belirle.
* In-memory görev listesi oluştur.
* ID üretme yaklaşımını belirle.
* Başlangıç demo verisi oluştur.

## Backlog 4.2 — CRUD işlemleri

**Öncelik:** P1
**Tahmini süre:** 1 gün
**Bağımlılık:** Uygulama iskeleti

### Task 4.2.1 — Görev listeleme

Sub-task’ler:

* `GET /tasks` endpoint’i oluştur.
* Tüm görevleri döndür.
* Boş liste durumunu test et.

### Task 4.2.2 — Görev ekleme

Sub-task’ler:

* `POST /tasks` endpoint’i oluştur.
* Başlık kontrolü yap.
* Yeni ID oluştur.
* Görevi listeye ekle.
* Geçersiz veri durumunu test et.

### Task 4.2.3 — Görev güncelleme

Sub-task’ler:

* `PUT /tasks/<id>` endpoint’i oluştur.
* Görevin varlığını kontrol et.
* Başlık ve durum alanlarını güncelle.
* Bulunamayan görev durumunu test et.

### Task 4.2.4 — Görev silme

Sub-task’ler:

* `DELETE /tasks/<id>` endpoint’i oluştur.
* Görevin varlığını kontrol et.
* Görevi listeden kaldır.
* Bulunamayan görev durumunu test et.

## Backlog 4.3 — Minimal frontend

**Öncelik:** P1
**Tahmini süre:** 1 gün
**Bağımlılık:** CRUD endpointleri

### Task 4.3.1 — Ana sayfa

Sub-task’ler:

* `templates` klasörünü oluştur.
* Görev listesini HTML’de göster.
* Yeni görev formu ekle.
* Tamamlandı bilgisini göster.

### Task 4.3.2 — Temel stil

Sub-task’ler:

* `static` klasörünü oluştur.
* Basit CSS dosyası ekle.
* Formu okunabilir hale getir.
* Liste görünümünü düzenle.

## Backlog 4.4 — Bilerek problemli kod örnekleri

**Öncelik:** P1
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Uygulamanın çalışması

### Task 4.4.1 — Statik analiz bulguları

Sub-task’ler:

* Demo TODO yorumu ekle.
* Bir uzun fonksiyon ekle.
* Bir boş except bloğu ekle.
* İsimlendirme hatası ekle.
* Sahte hardcoded secret örneği ekle.
* Gerçek secret kullanma.
* Her problemin beklenen kural ile eşleştiğini doğrula.

### Task 4.4.2 — Vulnerable dependency

Sub-task’ler:

* Gerçek advisory kaydı bulunan paket seç.
* Etkilenen gerçek sürümü doğrula.
* Kaynağı belgeye ekle.
* Paketi yalnızca kontrollü demo amacıyla requirements dosyasına ekle.
* Uygulama çalıştırılırken risk oluşup oluşmadığını değerlendir.
* Gerekirse bağımlılığı yalnızca test fixture içinde kullan.

## Backlog 4.5 — Entegrasyon

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Demo uygulaması

### Task 4.5.1 — Statik analiz entegrasyonu

Sub-task’ler:

* Statik analiz aracını `sample_app` üzerinde çalıştır.
* Beklenen bulguları listele.
* Dosya ve satır numaralarını doğrula.
* JSON raporu oluştur.
* Beklenmeyen false positive sonuçları incele.

### Task 4.5.2 — CVE tarama entegrasyonu

Sub-task’ler:

* Bağımlılık tarayıcıyı örnek requirements dosyasında çalıştır.
* Gerçek advisory kaydının bulunduğunu doğrula.
* Güvenli sürüm bilgisini kontrol et.
* JSON raporu oluştur.
* Kaynak bilgisini doğrula.

### Task 4.5.3 — Demo senaryosu

Sub-task’ler:

* Uygulamayı çalıştırma komutunu yaz.
* Statik analiz komutunu yaz.
* CVE tarama komutunu yaz.
* Beklenen örnek çıktıları belgeye ekle.
* Demo sırasını belirle.

## Hafta 4 teslimleri

* Çalışan Flask CRUD uygulaması
* Minimal frontend
* Bilerek eklenmiş statik analiz problemleri
* Gerçek advisory ile eşleşen demo bağımlılığı
* Statik analiz raporu
* CVE tarama raporu
* Entegrasyon testleri
* Pull Request
* Haftalık rapor

# 10. Hafta 5 — CI/CD, Test, Dokümantasyon ve Sunum

## Haftalık hedef

Araçları GitHub Actions pipeline’a eklemek, eksik testleri tamamlamak, dokümantasyonu güncellemek ve projeyi sunuma hazır hale getirmek.

## Backlog 5.1 — GitHub Actions kurulumu

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** İki analiz aracının çalışması

### Task 5.1.1 — Workflow dosyası

Sub-task’ler:

* `.github/workflows` klasörünü oluştur.
* `ci.yml` dosyasını oluştur.
* Pull Request tetikleyicisini ekle.
* `main` branch push tetikleyicisini ekle.

### Task 5.1.2 — Python ortamı

Sub-task’ler:

* Repository checkout adımını ekle.
* Python 3.11 kurulum adımını ekle.
* Pip güncelleme adımını ekle.
* Geliştirme bağımlılıklarını kur.

### Task 5.1.3 — Test adımı

Sub-task’ler:

* `pytest` komutunu çalıştır.
* Test başarısızsa pipeline’ı durdur.
* Test sonuçlarını okunabilir göster.

## Backlog 5.2 — Statik analiz pipeline entegrasyonu

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Workflow kurulumu

### Task 5.2.1 — Araç kodunun analizi

Sub-task’ler:

* Statik analiz aracını kendi kaynak kodunda çalıştır.
* Bağımlılık tarayıcı kaynak kodunu analiz et.
* `HIGH` veya `CRITICAL` bulguda pipeline’ı başarısız yap.
* JSON raporu oluştur.

### Task 5.2.2 — Demo uygulamasının analizi

Sub-task’ler:

* Demo uygulamasını statik analiz aracında çalıştır.
* Beklenen bulguları raporla.
* Bilerek eklenen bulgular nedeniyle pipeline’ın sürekli başarısız olmasını engelle.
* Demo bulgularını entegrasyon testiyle doğrulamayı değerlendir.

## Backlog 5.3 — CVE tarama pipeline entegrasyonu

**Öncelik:** P0
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Workflow kurulumu

### Task 5.3.1 — Bağımlılık taraması

Sub-task’ler:

* Bağımlılık tarayıcı CLI komutunu pipeline’a ekle.
* Kritik bulgu eşiğini belirle.
* JSON raporu oluştur.
* API erişilemezse davranışı belirle.
* CI için yerel fixture kullanımını değerlendir.

## Backlog 5.4 — Raporların saklanması

**Öncelik:** P2
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Pipeline raporları

### Task 5.4.1 — Artifact yükleme

Sub-task’ler:

* Statik analiz JSON raporunu sakla.
* CVE tarama JSON raporunu sakla.
* GitHub Actions artifact adımını ekle.
* Rapor dosyası bulunmadığında pipeline davranışını kontrol et.

## Backlog 5.5 — Eksik testlerin tamamlanması

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** Tüm ana bileşenler

### Task 5.5.1 — Test kapsam kontrolü

Sub-task’ler:

* Test edilmemiş kuralları belirle.
* CLI hata durumlarını test et.
* Exit code testlerini tamamla.
* JSON rapor testlerini tamamla.
* OSV hata testlerini tamamla.
* Demo entegrasyon testlerini tamamla.

### Task 5.5.2 — Kendi aracını kendi kodunda çalıştırma

Sub-task’ler:

* Statik analiz aracını tüm proje üzerinde çalıştır.
* Gerçek bulguları düzelt.
* Bilinen false positive sonuçları belgeye ekle.
* Son tarama raporunu sakla.

## Backlog 5.6 — README ve kullanım dokümantasyonu

**Öncelik:** P0
**Tahmini süre:** 1 gün
**Bağımlılık:** CLI komutlarının kesinleşmesi

### Task 5.6.1 — Kurulum

Sub-task’ler:

* Repository klonlama adımını yaz.
* Sanal ortam oluşturma adımını yaz.
* Windows CMD aktivasyonunu yaz.
* PowerShell aktivasyonunu yaz.
* Linux aktivasyonunu yaz.
* Bağımlılık kurulumunu yaz.

### Task 5.6.2 — Statik analiz kullanımı

Sub-task’ler:

* Temel komutu yaz.
* JSON çıktı komutunu yaz.
* Fail-on komutunu yaz.
* Parametreleri tablo halinde açıkla.
* Örnek terminal çıktısı ekle.

### Task 5.6.3 — CVE tarama kullanımı

Sub-task’ler:

* Temel komutu yaz.
* JSON çıktı komutunu yaz.
* Fail-on komutunu yaz.
* OSV ve yerel veri kullanımını açıkla.
* Örnek çıktı ekle.

### Task 5.6.4 — Bilinen sınırlamalar

Sub-task’ler:

* Yalnızca Python desteğini yaz.
* Requirements formatı sınırlamalarını yaz.
* False positive risklerini yaz.
* API bağımlılığını yaz.
* Güvenli sürüm bilgisinin her zaman bulunmayabileceğini yaz.

## Backlog 5.7 — Son teknik dokümantasyon

**Öncelik:** P1
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Uygulamanın son hali

### Task 5.7.1 — Doküman güncellemeleri

Sub-task’ler:

* Kapsam dokümanını gerçekleşen kapsama göre güncelle.
* Analiz dokümanını güncelle.
* Teknik tasarımı gerçek mimariye göre güncelle.
* Proje planında tamamlanan ve tamamlanmayan işleri işaretle.
* Mimari kararları güncelle.

## Backlog 5.8 — Demo ve sunum

**Öncelik:** P1
**Tahmini süre:** 0,5 gün
**Bağımlılık:** Projenin tamamlanması

### Task 5.8.1 — Demo hazırlığı

Sub-task’ler:

* Temiz bir terminal aç.
* Statik analiz komutunu hazırla.
* CVE tarama komutunu hazırla.
* GitHub Actions çalışmasını hazırla.
* JSON raporlarını hazırla.
* Olası internet problemi için yerel demo verisini hazırla.

### Task 5.8.2 — Sunum akışı

Sub-task’ler:

* Problemi açıkla.
* Proje kapsamını anlat.
* Mimarinin nasıl çalıştığını göster.
* Regex ve AST kararlarını açıkla.
* Statik analiz demosu yap.
* CVE tarama demosu yap.
* Pipeline sonucunu göster.
* Karşılaşılan riskleri ve öğrendiklerini anlat.
* Opsiyonel geliştirmeleri belirt.

## Hafta 5 teslimleri

* GitHub Actions pipeline
* Unit ve entegrasyon testleri
* Statik analiz JSON raporu
* CVE tarama JSON raporu
* Güncel README
* Güncel teknik dokümanlar
* Demo senaryosu
* Son Pull Request
* Proje sunumu
* Son haftalık rapor

# 11. İşler Arası Bağımlılıklar

Ana bağımlılık sırası:

```text
Kapsam Analizi
      |
      v
Gereksinim Analizi
      |
      v
Teknik Tasarım
      |
      v
Statik Analiz Çekirdeği
      |
      v
Statik Analiz Kuralları
      |
      +-------------------+
      |                   |
      v                   v
CVE Tarayıcı        Örnek Uygulama
      |                   |
      +---------+---------+
                |
                v
           Entegrasyon
                |
                v
         GitHub Actions
                |
                v
      Son Test ve Dokümantasyon
```

Önemli bağımlılıklar:

* Kural geliştirmeden önce Finding modeli hazırlanmalıdır.
* Scanner geliştirmeden önce kural arayüzü belirlenmelidir.
* JSON reporter geliştirmeden önce veri modeli belirlenmelidir.
* CVE eşleştirmeden önce requirements parser hazırlanmalıdır.
* CVE tarayıcı testlerinden önce gerçek advisory fixture hazırlanmalıdır.
* Demo uygulama entegrasyonundan önce iki araç temel seviyede çalışmalıdır.
* GitHub Actions entegrasyonundan önce CLI ve exit code sistemi tamamlanmalıdır.
* README son hali CLI komutları kesinleşince yazılmalıdır.

# 12. Riskler ve Çözüm Önerileri

## Risk 1 — Kapsamın büyümesi

Açıklama:

Statik analiz, CVE tarama, web uygulaması, test ve CI/CD birlikte düşünüldüğünde beş haftalık süre için kapsam büyüyebilir.

Çözüm:

* Önce minimum tamamlanabilir proje kapsamını geliştir.
* P2 ve P3 işleri sona bırak.
* Her hafta sonunda kalan işleri tekrar önceliklendir.
* Zorunlu olmayan API ve HTML rapor gibi özelliklere erken başlama.

## Risk 2 — AST yapısının karmaşık olması

Açıklama:

Python AST düğümleri ilk aşamada anlaşılması zor olabilir.

Çözüm:

* Küçük kod örnekleri üzerinde çalış.
* `ast.dump()` ile oluşan ağacı incele.
* Her kuralı ayrı prototip olarak başlat.
* Birden fazla kuralı aynı anda geliştirme.

## Risk 3 — Regex false positive üretmesi

Açıklama:

Regex, yorum, string ve gerçek kod arasındaki farkı her zaman anlayamaz.

Çözüm:

* Regex’i yalnızca metinsel kurallarda kullan.
* Yapısal kontrollerde AST kullan.
* Pozitif ve negatif test örneklerini artır.
* Bilinen false positive durumlarını dokümante et.

## Risk 4 — Hardcoded secret kuralının yanlış sonuç üretmesi

Açıklama:

`password = "test"` gibi eğitim amaçlı değerler ile gerçek secret değerleri ayırmak zordur.

Çözüm:

* Şüpheli değişken ismi ve sabit string atamasını birlikte kontrol et.
* Environment variable kullanımını temiz kabul et.
* Değerin kendisini rapora yazma.
* Kuralın kesin güvenlik açığı değil olası bulgu ürettiğini belirt.

## Risk 5 — CVE verisinin hatalı veya uydurma olması

Açıklama:

Yanlış CVE kimliği veya etkilenen sürüm bilgisi aracın güvenilirliğini bozar.

Çözüm:

* Verileri yalnızca OSV, GitHub Advisory Database veya NVD’den al.
* AI ile CVE verisi üretme.
* Yerel fixture içinde kaynak bilgisini sakla.
* Test verisinin orijinal kaydını belgeye ekle.

## Risk 6 — OSV servisine erişilememesi

Açıklama:

İnternet veya servis problemi taramayı durdurabilir.

Çözüm:

* HTTP timeout kullan.
* Kontrollü hata mesajı üret.
* Unit testlerde yerel fixture kullan.
* Demo için çevrimdışı veri hazırla.
* Pipeline’da canlı API bağımlılığını azalt.

## Risk 7 — Sürüm karşılaştırmasının yanlış yapılması

Açıklama:

Sürüm değerlerini string olarak karşılaştırmak hatalı sonuç üretebilir.

Çözüm:

* `packaging.version.Version` kullan.
* Sınır durumları için test yaz.
* Geçersiz sürüm değerlerini kontrollü şekilde raporla.

## Risk 8 — Demo bağımlılığının gerçek risk oluşturması

Açıklama:

Bilinen güvenlik açığı bulunan eski paketi doğrudan çalıştırmak güvenlik riski oluşturabilir.

Çözüm:

* Paketi yalnızca analiz fixture’ı olarak tutmayı değerlendir.
* Uygulamanın çalışması için zorunlu hale getirme.
* İzole sanal ortam kullan.
* Açığın türünü ve çalıştırma riskini gerçek kaynaktan incele.

## Risk 9 — Pipeline’ın sürekli başarısız olması

Açıklama:

Bilerek problemli demo uygulaması, statik analiz nedeniyle her Pull Request’i başarısız yapabilir.

Çözüm:

* Araç kaynak kodunu sıkı eşikle analiz et.
* Demo uygulamasını yalnızca rapor modunda analiz et.
* Demo için beklenen bulgu sayısını entegrasyon testiyle doğrula.

## Risk 10 — AI ile üretilen kodun anlaşılamaması

Açıklama:

Kod çalışsa bile geliştirici kodun neden o şekilde yazıldığını açıklayamayabilir.

Çözüm:

* Her fonksiyonun görevini kendi cümlelerinle açıkla.
* AI kodunu test etmeden commit etme.
* Bilinmeyen modül ve fonksiyonları araştır.
* PR açıklamasında yoğun AI kullanılan alanları belirt.
* Açıklayamadığın kodu sadeleştir veya yeniden yaz.

## Risk 11 — Git ve Pull Request sürecinde hata

Açıklama:

Yanlış branch üzerinde çalışma veya değişiklikleri push etmeyi unutma mümkündür.

Çözüm:

* Her işe başlamadan branch adını kontrol et.
* Küçük commit’ler oluştur.
* Commit sonrası Push origin yap.
* Pull Request açmadan önce dosya değişikliklerini kontrol et.
* Doğrudan main üzerinde özellik geliştirme.

# 13. Minimum Tamamlanabilir Proje Kapsamı

Zaman yetersiz kalırsa aşağıdaki özellikler mutlaka tamamlanmalıdır:

## Statik analiz

* Python klasörü tarama
* `.py` dosyalarını bulma
* TODO/FIXME kuralı
* Uzun fonksiyon kuralı
* Boş except kuralı
* Dosya adı ve satır numarası
* Terminal çıktısı
* JSON çıktısı
* Exit code
* Temel unit testler

## Bağımlılık tarama

* `requirements.txt` okuma
* `package==version` formatı
* Gerçek OSV verisi kullanımı
* En az bir gerçek advisory tespiti
* Paket ve kullanılan sürüm raporu
* Advisory veya CVE kimliği
* Güvenli sürüm mevcutsa raporlama
* Terminal ve JSON çıktısı
* Exit code
* Temel unit testler

## Örnek uygulama

* Basit Flask uygulaması
* En az temel listeleme ve ekleme işlemleri
* In-memory veri
* Statik analiz aracının bulacağı örnek problemler
* CVE tarayıcının kontrol edeceği requirements dosyası

## CI/CD

* GitHub Actions
* Unit testleri çalıştırma
* Statik analiz aracını çalıştırma
* CVE tarama aracını çalıştırma
* Kritik veya yüksek eşik davranışı

## Dokümantasyon

* Kurulum
* Kullanım
* Mimari
* Örnek komutlar
* Bilinen sınırlamalar
* Demo senaryosu

# 14. Opsiyonel Geliştirmeler

Zaman kalması durumunda aşağıdaki işler yapılabilir:

## P2 geliştirmeler

* Uzun sınıf kuralı
* Çıplak except kuralı
* `eval` ve `exec` kullanımı tespiti
* Renkli terminal çıktısı
* Konfigürasyon dosyası
* Daha gelişmiş exclude sistemi
* `pyproject.toml` bağımlılık okuma
* Birden fazla requirements dosyası
* Pipeline artifact raporları

## P3 geliştirmeler

* HTML raporu
* SARIF çıktısı
* GitHub Code Scanning entegrasyonu
* HTTP API endpoint
* Docker desteği
* Paralel dosya tarama
* Sonuç cache sistemi
* Baseline karşılaştırması
* Önceki rapor ile yeni rapor farkı
* Web tabanlı sonuç ekranı
* Otomatik düzeltme önerileri
* Plugin tabanlı kural sistemi

# 15. Haftalık Rapor Formatı

Her cuma aşağıdaki başlıklarla kısa rapor hazırlanacaktır:

```markdown
# Haftalık Rapor

## Ne yaptım?

## Ne öğrendim?

## Nerede takıldım?

## Önümüzdeki hafta ne yapacağım?
```

Rapor kısa, açık ve gerçek durumu yansıtacak şekilde hazırlanacaktır.

# 16. Günlük Çalışma Düzeni

Her gün çalışmaya başlarken:

1. Doğru branch üzerinde olduğunu kontrol et.
2. O gün tamamlanacak bir veya iki küçük task seç.
3. Büyük task’ı sub-task’lere ayır.
4. Kod yazmadan önce beklenen davranışı yaz.
5. Küçük testlerle ilerle.
6. Çalışan değişiklikleri commit et.
7. Takıldığında uzun süre tek başına uğraşmadan soru sor.

Gün sonunda:

1. Testleri çalıştır.
2. Değişiklikleri kontrol et.
3. Anlaşılır commit mesajı yaz.
4. Push origin yap.
5. Tamamlanan ve kalan işleri not et.

# 17. İlk Hafta İçin Günlük Plan

## Pazartesi

* Repository oluşturma
* GitHub Desktop bağlantısı
* README oluşturma
* `.gitignore` oluşturma
* Branch çalışma düzeni
* `scope.md` dosyasına başlama

## Salı

* `scope.md` dosyasını tamamlama
* `analysis.md` fonksiyonel gereksinimler
* `analysis.md` fonksiyonel olmayan gereksinimler
* Hata senaryoları

## Çarşamba

* Kabul kriterleri
* Statik analiz kuralları tablosu
* CVE tarama alternatifleri
* Seçilen hibrit yaklaşım

## Perşembe

* `technical-design.md`
* Sistem mimarisi
* Klasör yapısı
* Modül sorumlulukları
* Veri modelleri
* CLI tasarımı

## Cuma

* `project-plan.md`
* AST prototipi
* Prototip testi
* Doküman kontrolü
* Pull Request açma
* Haftalık rapor hazırlama

# 18. Başarı Ölçütleri

Proje sonunda aşağıdaki sorulara olumlu cevap verilebilmelidir:

* Python klasörü başarıyla taranabiliyor mu?
* Statik analiz kuralları doğru bulgu üretiyor mu?
* Temiz kodda yanlış bulgu sayısı kabul edilebilir mi?
* Requirements dosyası doğru okunuyor mu?
* Gerçek advisory verisi doğru raporlanıyor mu?
* CVE verisinin kaynağı gösteriliyor mu?
* Terminal ve JSON çıktıları çalışıyor mu?
* Exit code pipeline tarafından kullanılabiliyor mu?
* Unit testler başarıyla çalışıyor mu?
* Araç kendi kodunu analiz edebiliyor mu?
* GitHub Actions Pull Request sırasında çalışıyor mu?
* Projenin kurulumu ve kullanımı dokümante edilmiş mi?
* Geliştirici teslim ettiği kodu açıklayabiliyor mu?
