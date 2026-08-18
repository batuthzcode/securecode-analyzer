# SecureCode Analyzer

[![CI](https://github.com/batuthzcode/securecode-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/batuthzcode/securecode-analyzer/actions/workflows/ci.yml)

SecureCode Analyzer, Python projeleri için iki bağımsız komut satırı aracı ve
bu araçların kontrollü olarak gösterildiği küçük bir Flask uygulaması içerir:

- Python kaynaklarını AST ve metin kurallarıyla inceleyen static analyzer
- Exact-pinned Python bağımlılıklarını OSV verisiyle eşleştiren vulnerability
  scanner
- Gerçek credential içermeyen, çalışan uygulamadan izole güvenlik demo
  fixture'ları

Proje Python `3.11+` destekler. Mevcut doğrulama paketi 1.065 test, `%98,6`
birleşik statement/branch coverage, whole-project self-analysis ve offline OSV
entegrasyon kontrolü içerir.

## Özellikler

- Alt dizinleri özyinelemeli tarayan Python dosya keşfi
- Altı yerleşik static-analysis kuralı
- İnsan tarafından okunabilir text ve makine tarafından okunabilir JSON çıktı
- CI kullanımına uygun `0`, `1` ve `2` exit code sözleşmesi
- Static analyzer için `any`, `info`, `warning`, `error` severity eşikleri
- Dependency scanner için `any`, `low`, `medium`, `high`, `critical` eşikleri
- PyPI paketleri için canlı OSV query desteği
- CVSS v3 base-score hesaplama ve qualitative severity sınıflandırması
- Deterministik offline OSV fixture akışı
- GitHub Actions test, coverage, static-analysis ve dependency-scan gate'leri
- Canonical JSON raporlar ve 14 günlük Actions artifact'ları

## Mimari

```text
Python source directory
  -> FileScanner
  -> SourceReader
  -> AnalysisEngine
  -> SA001 ... SA006
  -> text / JSON report

requirements.txt
  -> requirements parser
  -> DependencyScanner
  -> OsvVulnerabilitySource
  -> OsvQueryClient
  -> text / JSON report
```

Üç ana bileşenin ayrıntılı dokümanları:

- [Static Code Analyzer](docs/components/static-analyzer/README.md)
- [Dependency Scanner](docs/components/dependency-scanner/README.md)
- [Sample Web Application](docs/components/sample-web-app/README.md)

## Static Analysis Kuralları

| Rule ID | Kural | Varsayılan severity | Davranış |
|---|---|---|---|
| `SA001` | Long Function | `WARNING` | 50 satırı aşan fonksiyonları bulur. |
| `SA002` | Long Class | `WARNING` | 200 satırı aşan sınıfları bulur. |
| `SA003` | TODO/FIXME | `INFO` / `WARNING` | Yorumlardaki TODO ve FIXME işaretlerini bulur. |
| `SA004` | Empty Except | `WARNING` | Yalnızca `pass` içeren exception handler'ları bulur. |
| `SA005` | Hardcoded Secret | `WARNING` | Hassas isimli değişkenlere atanan string literal değerleri işaretler. |
| `SA006` | Naming Convention | `INFO` | Fonksiyonlarda `snake_case`, sınıflarda `PascalCase` kontrol eder. |

`SA005` secret değerini rapora yazmaz; yalnızca genel bir bulgu mesajı üretir.

## Kurulum

### 1. Repository'yi klonla

```text
git clone https://github.com/batuthzcode/securecode-analyzer.git
cd securecode-analyzer
```

### 2. Sanal ortam oluştur

```text
python -m venv .venv
```

Windows Command Prompt aktivasyonu:

```bat
.venv\Scripts\activate.bat
```

Windows PowerShell aktivasyonu:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux ve macOS aktivasyonu:

```bash
source .venv/bin/activate
```

### 3. Paketi kur

Yalnızca iki analiz aracını kurmak için:

```text
python -m pip install --upgrade pip
python -m pip install -e .
```

Test, coverage ve sample app bağımlılıklarıyla geliştirme kurulumu:

```text
python -m pip install -e ".[dev]"
```

Yalnızca Flask demo bağımlılığını eklemek için `.[sample-app]` extra değeri de
kullanılabilir. Kurulumu kontrol et:

```text
securecode-analyzer --help
securecode-dependency-scan --help
```

## Static Analyzer Kullanımı

### Temel tarama

Bir Python kaynak klasörünü text formatında tara:

```text
securecode-analyzer src
```

Repository'nin tamamını tara:

```text
securecode-analyzer .
```

### JSON çıktı

```text
securecode-analyzer src --format json
```

CLI çıktıyı stdout'a yazar. JSON raporunu dosyada saklamak için shell
redirection kullanılabilir:

```powershell
New-Item -ItemType Directory -Force reports\local
securecode-analyzer src --format json > reports\local\static-analysis.json
```

### Severity gate

Varsayılan `--fail-on any`, severity değerinden bağımsız olarak her bulguda
exit code `1` üretir. Yalnızca `WARNING` veya `ERROR` bulgularında başarısız
olmak için:

```text
securecode-analyzer src --fail-on warning
```

Yalnızca `ERROR` bulgularını pipeline hatası yapmak için:

```text
securecode-analyzer src --format json --fail-on error
```

Severity sırası:

```text
info < warning < error
```

### Parametreler

| Parametre | Zorunlu | Varsayılan | Açıklama |
|---|---:|---|---|
| `target` | Evet | — | Analiz edilecek Python kaynak klasörü. |
| `--format` | Hayır | `text` | `text` veya `json`. |
| `--fail-on` | Hayır | `any` | `any`, `info`, `warning` veya `error`. |
| `-h`, `--help` | Hayır | — | CLI yardımını gösterir. |

### Örnek terminal çıktısı

```text
[WARNING] SA005 src/example.py:1:1 - Possible hardcoded secret found.

1 finding found.
```

Temiz tarama çıktısı:

```text
No findings found.
```

### Exit code sözleşmesi

| Exit code | Anlam |
|---:|---|
| `0` | Analiz tamamlandı ve seçilen eşiği karşılayan bulgu yok. |
| `1` | Analiz tamamlandı ve seçilen eşiği karşılayan bulgu var. |
| `2` | Hedef, dosya okuma, Unicode veya Python syntax hatası oluştu. |

Rapor, threshold altında kalan bulguları da göstermeye devam eder; `--fail-on`
yalnızca process exit code değerini değiştirir.

## Dependency Scanner Kullanımı

Dependency scanner yalnızca exact pin biçimindeki aktif satırları kabul eder:

```text
Flask==3.1.3
```

### Canlı OSV taraması

```text
securecode-dependency-scan requirements.txt
```

Bu komut `https://api.osv.dev/v1/query` endpoint'ine her dependency için
package, `PyPI` ecosystem ve version bilgisiyle POST isteği gönderir.

### JSON çıktı ve rapor dosyası

```text
securecode-dependency-scan requirements.txt --format json
```

CLI'ın kendi `--output` seçeneğiyle UTF-8 rapor yaz:

```powershell
New-Item -ItemType Directory -Force reports\local
securecode-dependency-scan requirements.txt `
  --format json `
  --output reports\local\dependency-scan.json
```

Output dosyasının parent klasörü önceden bulunmalıdır. Input requirements
dosyasının output hedefi olarak seçilmesi güvenlik amacıyla reddedilir.

### Severity gate

Varsayılan politika bütün bulgularda başarısız olur:

```text
securecode-dependency-scan requirements.txt --fail-on any
```

Yalnızca `HIGH` ve `CRITICAL` bulguları gate hatası yapmak için:

```text
securecode-dependency-scan requirements.txt --fail-on high
```

Severity sırası:

```text
unknown | low < medium < high < critical
```

`UNKNOWN` yalnızca `--fail-on any` politikasıyla exit code `1` üretir.

### Parametreler

| Parametre | Zorunlu | Varsayılan | Açıklama |
|---|---:|---|---|
| `requirements_file` | Evet | — | Taranacak UTF-8 requirements dosyası. |
| `--format` | Hayır | `text` | `text` veya `json`. |
| `--output` | Hayır | stdout | Raporun yazılacağı mevcut parent'a sahip dosya yolu. |
| `--fail-on` | Hayır | `any` | `any`, `low`, `medium`, `high` veya `critical`. |
| `--source` | Hayır | `osv` | Vulnerability source; şu anda yalnızca `osv`. |
| `--timeout` | Hayır | `10.0` | Pozitif ve finite OSV timeout süresi. |
| `-h`, `--help` | Hayır | — | CLI yardımını gösterir. |

### Örnek terminal çıktısı

```text
[HIGH] PYSEC-2024-38 fastapi==0.109.0 sample_app/requirements-vulnerable.txt:6 - Affected dependency. | source=OSV | fixed=0.109.1 | aliases=CVE-2024-24762

1 dependency scanned. 1 finding. 0 lookup errors.
```

Gerçek OSV mesajı ve alias listesi upstream advisory verisine göre daha uzun
olabilir.

### Yerel OSV verisi

Canlı OSV verisi zaman içinde değişebilir ve ağ erişimi gerektirir. Repository,
CI ve demo için provenance bilgisi içeren deterministik bir fixture sağlar:

```powershell
python -m tools.run_ci_dependency_scan `
  --requirements sample_app/requirements-vulnerable.txt `
  --fixture tests/fixtures/osv/fastapi-0.109.0.json `
  --output reports/ci/dependency-scan.json `
  --fail-on critical
```

Bu yardımcı araç production requirements parser, dependency scanner, OSV
response parser, source mapping ve JSON formatter katmanlarını kullanır; HTTP
isteği göndermez. Fixture yalnızca kaydedilmiş `fastapi==0.109.0` sorgusunu
cevaplar ve genel amaçlı offline vulnerability database değildir.

### Exit code sözleşmesi

| Exit code | Anlam |
|---:|---|
| `0` | Tarama tamamlandı ve seçilen eşiği karşılayan bulgu yok. |
| `1` | Tarama tamamlandı ve seçilen eşiği karşılayan bulgu var. |
| `2` | Dosya, parse, output, OSV network/response veya lookup hatası var. |

Bir lookup hatası oluşursa exit code `2`, finding eşiğinden önceliklidir.
Başarılı ve başarısız lookup kayıtları aynı kısmi raporda korunur.

## Sample Web Application

Flask demo uygulamasını repository kökünden çalıştır:

```text
python -m pip install -e ".[sample-app]"
flask --app sample_app run --debug
```

Ardından `http://127.0.0.1:5000` adresini aç. Uygulama in-memory task CRUD
akışı sağlar; veriler process kapandığında silinir.

Kontrollü güvenlik demosu:

```text
securecode-analyzer sample_app --format text
securecode-dependency-scan sample_app/requirements-vulnerable.txt --fail-on high
```

Static komut tam olarak beş kasıtlı bulgu, dependency komutu canlı OSV verisi
uygunsa `PYSEC-2024-38` kaydını üretir. Vulnerable FastAPI pini normal Flask
runtime requirements dosyasından ayrıdır ve uygulamayı çalıştırmak için
kurulmaz.

Deterministik demo raporlarını kontrol et:

```text
python -m tools.generate_sample_app_reports --check
python -m tools.generate_self_analysis_report --check
```

## Test ve CI

Tam paketi branch coverage gate'iyle çalıştır:

```text
python -m coverage run -m pytest -q
python -m coverage report
```

CI minimum birleşik statement/branch coverage değerini `%97` olarak zorunlu
tutar. GitHub Actions Pull Request ve `main` push olaylarında şu job'ları
çalıştırır:

1. Python 3.11 test ve coverage gate'i
2. Static analyzer kaynak, araç, demo ve whole-project report kontrolü
3. Offline OSV dependency vulnerability gate'i

Static ve dependency JSON raporları Actions artifact'ı olarak 14 gün saklanır.
Ayrıntılar için [GitHub Actions CI](docs/ci.md) dokümanına bakın.

## Bilinen Sınırlamalar

- Static analyzer yalnızca Python `.py` dosyalarını ve klasör hedeflerini
  destekler; JavaScript, Java, Go ve diğer diller kapsam dışıdır.
- Kurallar seçilmiş AST/metin kalıplarına dayanır. Dinamik veri akışı,
  interprocedural taint analysis ve runtime davranışı analiz edilmez.
- TODO/FIXME, naming ve hardcoded-secret kuralları heuristic olduğu için false
  positive veya false negative üretebilir. Finding'ler insan incelemesi
  gerektirir.
- Inline suppression, özel config dosyası, autofix, SARIF ve HTML raporu yoktur.
- Requirements parser yalnızca `package==version` biçimini, boş satırları ve
  tam satır yorumlarını destekler. Version range, environment marker, extras,
  recursive include, editable, VCS ve URL requirement değerleri desteklenmez.
- Dependency scanner yalnızca Python/PyPI paketlerini ve OSV source değerini
  destekler; `pyproject.toml`, lock file ve installed-environment keşfi yapmaz.
- Canlı tarama OSV API erişilebilirliğine ve mutable upstream veriye bağlıdır;
  retry ve cache uygulanmaz.
- OSV kaydında geçerli CVSS v3 vector yoksa severity `UNKNOWN`, eşleşen
  ecosystem fixed event yoksa güvenli sürüm bilgisi `null` kalabilir.
- Offline fixture yalnızca test ve demo için sabit bir OSV projection'dır;
  güncel güvenlik taramasının yerine geçmez.
- Sample app authentication, kalıcı database ve production deployment
  hardening sağlamaz.

## Güvenlik Notu

Bu araç eğitim ve temel otomasyon amacıyla geliştirilmiştir. Tek başına code
review, SAST/DAST platformu, dependency lock denetimi veya profesyonel
penetration testinin yerini almaz. Secret, token veya özel repository içeren
raporları paylaşmadan önce içeriği inceleyin.

## Dokümantasyon

- [Proje dokümantasyonu](docs/README.md)
- [Proje kapsamı](docs/scope.md)
- [Beş haftalık proje planı](docs/project-plan.md)
- [Whole-project self-analysis ve coverage](docs/self-analysis.md)
- [GitHub Actions CI](docs/ci.md)

## Geliştirme Akışı

Değişiklikler ayrı branch'lerde hazırlanır, test ve güvenlik gate'lerinden
geçen Pull Request'ler review sonrasında `main` branch'ine squash merge edilir.
