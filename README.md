## [Components](docs/components/README.md)

[Üç bileşenin genel listesini görüntüle](docs/components/README.md)

### 1. Static Code Analyzer

Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit eder.

[Static Code Analyzer bileşenini incele](docs/components/static-analyzer/README.md)

### 2. Dependency and CVE Scanner

Python projelerindeki bağımlılıkları inceleyerek bilinen güvenlik açıklarını tespit eder.

[Dependency and CVE Scanner bileşenini incele](docs/components/dependency-scanner/README.md)

### 3. Sample Web Application

Statik kod analiz aracının ve bağımlılık tarayıcısının test edileceği örnek Flask uygulamasıdır.

[Sample Web Application bileşenini incele](docs/components/sample-web-app/README.md)

## Documentation

[Proje dokümantasyonunu görüntüle](docs/README.md)

### Genel Proje Dokümanları

- [Proje Kapsamı](docs/scope.md)
- [Beş Haftalık Proje Planı](docs/project-plan.md)
- [GitHub Actions CI](docs/ci.md)

### Bileşen Dokümanları

- [Static Code Analyzer](docs/components/static-analyzer/README.md)
- [Dependency Scanner](docs/components/dependency-scanner/README.md)
- [Sample Web Application](docs/components/sample-web-app/README.md)

## Current Status

Birinci hafta kapsamında aşağıdaki çalışmalar yapılmıştır:

* Proje kapsamı hazırlandı.
* Fonksiyonel ve fonksiyonel olmayan gereksinimler belirlendi.
* Teknik tasarım dokümanı oluşturuldu.
* Beş haftalık proje planı hazırlandı.
* Proje üç ana bileşene ayrıldı.
* AST kullanılarak uzun fonksiyon tespiti yapan ilk prototip geliştirildi.

## Development Workflow

Her geliştirme ayrı bir branch üzerinde yapılmaktadır.

Değişiklikler Pull Request üzerinden incelenmekte ve reviewer tarafından ana branch ile birleştirilmektedir.
