# GitHub Actions CI

Bu doküman Backlog 5.1, 5.2, 5.3 ve 5.4 kapsamındaki test, statik analiz,
bağımlılık tarama ve rapor artifact pipeline'ının gereksinimlerini, güvenlik
sınırlarını ve çalışma sırasını açıklar.

## Mevcut Durum

GitHub Actions test, statik analiz, bağımlılık tarama ve güvenlik raporu
saklama workflow'u tamamlanmıştır:

```text
.github/workflows/ci.yml
```

Workflow Pull Request değişikliklerinde ve `main` branch push olaylarında
Python 3.11 test paketini çalıştırır. Test gate'i geçtikten sonra proje
kaynaklarını ve kontrollü demo uygulamasını ayrı bir static-analysis job'unda
tarar. Buna paralel dependency-scan job'u, checked-in OSV fixture ile kritik
güvenlik açığı gate'ini çalıştırır. İki güvenlik job'u ürettikleri doğrulanmış
JSON raporlarını 14 günlük GitHub Actions artifact'ları olarak saklar.

## Trigger Sözleşmesi

Pipeline aşağıdaki olaylarda çalışır:

- Her `pull_request` olayı
- Yalnızca `main` branch'ine yapılan `push` olayları

`pull_request_target` kullanılmaz. Böylece fork kaynaklı güvenilmeyen kod daha
yüksek yetkili base repository bağlamında çalıştırılmaz.

## İzin ve Çalıştırma Sınırları

Workflow-level `GITHUB_TOKEN` izni yalnızca şöyledir:

```yaml
permissions:
  contents: read
```

Checkout sonrasında credential persistence kapalıdır. Üç job da
`ubuntu-latest` runner üzerinde en fazla 10 dakika çalışır. Aynı workflow ve
Git ref için yeni bir run başladığında önceki run iptal edilir.

Bu job'lar secret, repository write permission, deployment environment veya
harici service credential kullanmaz. Artifact upload, GitHub Actions'ın job
çalışma bağlamındaki yerleşik artifact servisini kullanır.

## Action Pinleri

Supply-chain değişkenliğini azaltmak için action major tag'leri yerine release
commit SHA değerleri kullanılır:

| Action | Release | Commit |
|---|---|---|
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | `v7.0.0` | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/upload-artifact` | `v7.0.1` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |

Yorumdaki release etiketi bakım sırasında SHA provenance değerinin kolayca
kontrol edilmesini sağlar.

Resmî release kaynakları:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [actions/setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0)
- [actions/upload-artifact v7.0.1](https://github.com/actions/upload-artifact/releases/tag/v7.0.1)

## Test Job Akışı

Job sırası:

1. Repository'yi immutable `actions/checkout` SHA değeriyle checkout et.
2. Python `3.11` ortamını immutable `actions/setup-python` SHA değeriyle kur.
3. `pyproject.toml` anahtarına göre pip download cache'ini geri yükle.
4. Pip'i güncelle.
5. Projeyi `.[dev]` extra bağımlılıklarıyla editable kur.
6. `python -m pytest -q` komutunu çalıştır.

Install veya test komutlarından herhangi biri non-zero exit code üretirse job
ve workflow başarısız olur.

## Statik Analiz Job Akışı

`static-analysis` job'u test job'una `needs: test` ile bağlıdır. Başarılı test
sonrasında aynı sabit action SHA değerleri ve Python 3.11 ortamıyla çalışır.

Job aşağıdaki raporları üretir:

```text
reports/ci/static-analysis-src.json
reports/ci/static-analysis-tools.json
reports/ci/static-analysis-sample-app.json
```

`src` ve `tools` taramalarında herhangi bir bulgu CLI exit code `1` ürettiği
için job başarısız olur. Bu sıfır-bulgu politikası, proje planındaki yalnızca
yüksek önem seviyelerinde durma gereksiniminden daha katıdır. Statik analiz
modeli `INFO`, `WARNING` ve `ERROR` seviyelerini kullandığından `HIGH` ve
`CRITICAL` adları bu bileşene uygulanmaz.

`sample_app` bilerek eklenmiş beş bulgu içerir. Bu taramanın exit code `1`
üretmesi beklenir ve hata olarak değerlendirilmez. Üretilen JSON, checked-in
`reports/sample-app/static-analysis.json` baseline'ı ile byte düzeyinde
karşılaştırılır; ardından kontrollü demo entegrasyon testleri çalıştırılır.
Exit code veya baseline değişirse job başarısız olur.

## Bağımlılık Tarama Job Akışı

`dependency-scan` job'u test job'una bağlıdır ve statik analiz job'uyla
paralel çalışabilir. Aşağıdaki komut production dependency runner'ını yerel
OSV verisiyle çalıştırır:

```text
python -m tools.run_ci_dependency_scan
```

Workflow girdileri açıkça sabitlenmiştir:

```text
requirements: sample_app/requirements-vulnerable.txt
OSV fixture: tests/fixtures/osv/fastapi-0.109.0.json
report: reports/ci/dependency-scan.json
fail-on: critical
```

`tools/osv_fixture.py`, fixture metadata'sındaki package, ecosystem ve version
değerlerini doğrular ve yalnızca aynı query için cevap verir. Canlı HTTP
client oluşturulmaz. Fixture bulunamazsa, geçersizse, query eşleşmezse veya
scan error üretirse komut fail-closed davranarak exit code `2` döndürür.

Checked-in gerçek OSV kaydı `PYSEC-2024-38` / `CVE-2024-24762` için `HIGH`
severity üretir. CI eşiği `CRITICAL` olduğundan bu kontrollü bulgu raporlanır
ancak job'u başarısız yapmaz. Aynı veri `--fail-on high` ile exit code `1`
üretir; bu davranış testlerle korunur.

Üretilen JSON, `reports/sample-app/dependency-scan.json` baseline'ı ile byte
düzeyinde karşılaştırılır. Ardından offline CI ve production-layer dependency
entegrasyon testleri çalıştırılır. Böylece ağ erişilebilirliği pipeline
sonucunu etkilemez ve fixture drift'i sessizce kabul edilmez.

## Güvenlik Raporu Artifact Akışı

Raporlar üretildikleri job'dan doğrudan yüklenir. Böylece ayrı bir aggregation
job'u, job'lar arası geçici indirme veya genişletilmiş token izni gerekmez.

Her workflow attempt'i aşağıdaki iki artifact'ı oluşturur:

| Artifact | İçerik |
|---|---|
| `static-analysis-reports-${{ github.run_attempt }}` | `static-analysis-src.json`, `static-analysis-tools.json`, `static-analysis-sample-app.json` |
| `dependency-scan-report-${{ github.run_attempt }}` | `dependency-scan.json` |

Artifact adından `github.run_attempt` kullanılması, aynı workflow run'ı yeniden
çalıştırıldığında immutable artifact adlarının çakışmasını önler.

Upload öncesinde her gerekli dosya Bash `-s` kontrolüyle hem varlık hem boş
olmama açısından doğrulanır. Doğrulama ve upload adımları `!cancelled()`
koşuluyla normal başarıda ve önceki adım başarısız olduğunda çalışır; iptal
edilmiş run için eksik veya yarım artifact yayınlanmaz. Gerekli dosya eksik ya
da boşsa job başarısız kalır. `if-no-files-found: error` aynı davranışı action
seviyesinde ikinci kez korur ve `continue-on-error` kullanılmaz.

Her iki artifact 14 gün saklanır. Yalnızca makine tarafından okunabilir JSON
raporları yüklenir; source checkout, dependency cache, log veya credential
artifact kapsamına alınmaz. Upload action'ı diğer resmî action'lar gibi tam
commit SHA değerine sabitlenmiştir.

## Yerel Eşdeğer

CI test adımını yerelde doğrulamak için:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
```

Statik analiz adımlarını yerelde doğrulamak için:

```powershell
New-Item -ItemType Directory -Force reports/ci
securecode-analyzer src --format json `
  > reports/ci/static-analysis-src.json
securecode-analyzer tools --format json `
  > reports/ci/static-analysis-tools.json
securecode-analyzer sample_app --format json `
  > reports/ci/static-analysis-sample-app.json
python -m pytest tests/test_sample_app_security_demo.py -q
```

Demo komutunun beklenen exit code değeri `1` olmalıdır. Üretilen demo JSON'u
checked-in baseline ile birebir aynı olmalıdır.

Offline dependency gate'ini yerelde çalıştırmak için:

```powershell
python -m tools.run_ci_dependency_scan `
  --requirements sample_app/requirements-vulnerable.txt `
  --fixture tests/fixtures/osv/fastapi-0.109.0.json `
  --output reports/ci/dependency-scan.json `
  --fail-on critical
```

Başarılı kontrollü tarama exit code `0` üretir. Report, gerçek `HIGH` bulguyu
korur; `--fail-on high` kullanıldığında aynı komut exit code `1` döndürür.

Workflow sözleşmesi de normal test paketi içindedir:

```powershell
python -m pytest tests/test_ci_workflow.py -q
```

Minimum Python syntax sözleşmesini doğrulamak için:

```powershell
python -m pytest tests/test_python_compatibility.py -q
```

## Sözleşme Testleri

`tests/test_ci_workflow.py` aşağıdaki değerleri korur:

- Pull Request ve `main` push trigger'ları
- `pull_request_target` yasağı
- Salt-okunur repository permission
- Checkout credential persistence yasağı
- Concurrency cancellation
- Üç action için tam 40 karakterli SHA ve release etiketi
- Python 3.11 ve pip cache yapılandırması
- Pip upgrade, dev install ve pytest komut sırası
- Ubuntu runner ve 10 dakikalık timeout
- Test job'una bağlı statik analiz job'u
- `src`, `tools` ve `sample_app` JSON rapor yolları
- Kontrollü demo exit code ve baseline doğrulaması
- Test job'una bağlı offline dependency-scan job'u
- Açık requirements, fixture, output ve `critical` eşik değerleri
- Dependency baseline ve entegrasyon testi doğrulaması
- İki güvenlik artifact'ının ayrı, attempt-safe adları ve kesin dosya kapsamı
- Eksik/boş rapor için fail-closed kontrol ve `if-no-files-found: error`
- 14 günlük sınırlı saklama süresi ve iptal edilen run upload yasağı

`tests/test_python_compatibility.py`, `src`, `sample_app`, `tools` ve `tests`
altındaki bütün Python dosyalarını desteklenen en düşük sürüm olan Python
3.11 grameriyle ayrıştırır. Böylece daha yeni bir yorumlayıcıda yerel olarak
geçen Python 3.12+ söz dizimi değişiklikleri CI'a ulaşmadan tespit edilir.

Doğrulanan mevcut sonuç:

```text
CI workflow contract tests: 16 passed
Offline dependency CI tests: 6 passed
Python 3.11 compatibility tests: 1 passed
Complete test suite: 1000 passed
Workflow YAML parse check: passed
```

## Sonraki Güvenlik Job'ları

Backlog 5.1, 5.2, 5.3 ve 5.4 tamamlanmıştır. Sonraki aşama:

1. Backlog 5.5 kapsamında eksik test ve self-analysis kapsamını tamamlama

Bu ayrım her güvenlik gate'inin davranışını bağımsız olarak incelemeyi sağlar.

## Navigation

- [Proje dokümantasyonuna dön](README.md)
- [Tüm bileşenlere dön](components/README.md)
- [Projenin ana sayfasına dön](../README.md)
