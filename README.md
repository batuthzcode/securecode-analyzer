# Python Security Project

Python projelerinde kod kalitesi sorunlarını ve bağımlılık güvenlik açıklarını tespit etmeyi amaçlayan bir güvenlik projesidir.

Proje üç ana bileşenden oluşmaktadır:

## [Components](components/README.md)

[Üç bileşenin genel listesini görüntüle](components/README.md)

### 1. Static Code Analyzer

Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve güvenlik problemlerini tespit eder.

[Static Code Analyzer bileşenini incele](components/static-analyzer/README.md)

### 2. Dependency and CVE Scanner

Python projelerindeki bağımlılıkları inceleyerek bilinen güvenlik açıklarını tespit eder.

[Dependency and CVE Scanner bileşenini incele](components/dependency-scanner/README.md)

### 3. Sample Web Application

Statik kod analiz aracının ve bağımlılık tarayıcısının test edileceği örnek Flask uygulamasıdır.

[Sample Web Application bileşenini incele](components/sample-web-app/README.md)

## Documentation

Tüm proje ve bileşen dokümanlarına aşağıdaki sayfadan ulaşabilirsiniz:

[Proje dokümantasyonunu görüntüle](docs/README.md)

### Genel Proje Dokümanları

- [Proje Kapsamı](docs/scope.md)
- [Beş Haftalık Proje Planı](docs/project-plan.md)

### Bileşen Dokümanları

- [Static Code Analyzer](components/static-analyzer/README.md)
- [Dependency Scanner](components/dependency-scanner/README.md)
- [Sample Web Application](components/sample-web-app/README.md)

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
