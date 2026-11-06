# SecureCode Analyzer

[![CI](https://github.com/batuthzcode/securecode-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/batuthzcode/securecode-analyzer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

Python projeleri için geliştirilen statik kod analizi ve bağımlılık güvenliği
araç setidir. Kaynak kodu çalıştırmadan AST ve metin tabanlı kurallarla
inceleyebilir; sabitlenmiş Python bağımlılıklarını OSV verileriyle
karşılaştırabilir.

> Bu proje eğitim ve güvenli yazılım geliştirme çalışmaları için hazırlanmıştır.
> Bulgular tek başına kesin güvenlik açığı kararı olarak değerlendirilmemelidir.

## Özellikler

### Static Code Analyzer

- Python dosyalarını özyinelemeli tarama
- AST ve metin tabanlı kurallar
- Uzun fonksiyon/sınıf, TODO/FIXME, boş `except`, olası sabit anahtar ve
  isimlendirme kontrolleri
- Okunabilir terminal ve JSON çıktısı
- Sonuçlara göre otomasyona uygun exit code

### Dependency and CVE Scanner

- Sabitlenmiş `requirements.txt` girdilerini ayrıştırma
- Paket adı normalizasyonu
- OSV tabanlı güvenlik açığı sorgulama katmanı
- Terminal ve JSON raporu
- Çevrimdışı fixture'larla deterministik CI doğrulaması

### Sample Web Application

Kontrollü güvenlik bulguları içeren Flask örneği, analiz araçlarının davranışını
ve CI güvenlik kapılarını göstermek için kullanılır.

## Hızlı Başlangıç

Gereksinimler: Python 3.11 veya üzeri.

```powershell
git clone https://github.com/batuthzcode/securecode-analyzer.git
cd securecode-analyzer
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Bir Python projesini analiz etmek için:

```powershell
.\.venv\Scripts\securecode-analyzer.exe src
.\.venv\Scripts\securecode-analyzer.exe src --format json
```

Bağımlılık tarayıcısının güncel seçenekleri için:

```powershell
.\.venv\Scripts\securecode-dependency-scan.exe --help
```

Linux/macOS üzerinde komutlar etkin sanal ortamda `securecode-analyzer` ve
`securecode-dependency-scan` olarak çalıştırılabilir.

## Test ve Kalite

```powershell
.\.venv\Scripts\python.exe -m coverage run -m pytest -q
.\.venv\Scripts\python.exe -m coverage report
```

GitHub Actions; testleri, proje kaynaklarının kendi aracıyla statik analizini ve
çevrimdışı bağımlılık güvenliği kapısını çalıştırır. Coverage eşiği
`pyproject.toml` içinde %97 olarak tanımlıdır.

## Proje Yapısı

```text
src/static_analyzer/       Statik analiz motoru ve CLI
src/dependency_scanner/    Bağımlılık güvenliği bileşenleri
sample_app/                Kontrollü Flask güvenlik demosu
tests/                     Otomatik testler
docs/                      Tasarım ve bileşen belgeleri
reports/                   Tekrarlanabilir örnek raporlar
```

## Dokümantasyon

- [Dokümantasyon merkezi](docs/README.md)
- [Bileşenler](docs/components/README.md)
- [Statik analiz bileşeni](docs/components/static-analyzer/README.md)
- [Bağımlılık tarayıcısı](docs/components/dependency-scanner/README.md)
- [GitHub Actions CI](docs/ci.md)
- [Proje planı](docs/project-plan.md)

## Sınırlamalar

- Araç şu aşamada Python projelerine odaklanır.
- Statik analiz kuralları olası sorunları işaretler; manuel doğrulama gerekir.
- Dependency scanner ilk sürümde sabitlenmiş `==` bağımlılıklara odaklanır.
- Canlı OSV sorguları ağ erişimi ve hizmet kullanılabilirliğine bağlıdır.

## Lisans

[MIT](LICENSE)
