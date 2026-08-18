# GitHub Actions CI

Bu doküman Backlog 5.1 ve 5.2 kapsamındaki test ve statik analiz pipeline'ının
gereksinimlerini, güvenlik sınırlarını ve çalışma sırasını açıklar.

## Mevcut Durum

GitHub Actions test ve statik analiz workflow'u tamamlanmıştır:

```text
.github/workflows/ci.yml
```

Workflow Pull Request değişikliklerinde ve `main` branch push olaylarında
Python 3.11 test paketini çalıştırır. Test gate'i geçtikten sonra proje
kaynaklarını ve kontrollü demo uygulamasını ayrı bir static-analysis job'unda
tarar. Sıradaki aşama dependency scanner ve report artifact job'larıdır.

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

Checkout sonrasında credential persistence kapalıdır. Test ve statik analiz
job'ları `ubuntu-latest` runner üzerinde en fazla 10 dakika çalışır. Aynı
workflow ve Git ref için yeni bir run başladığında önceki run iptal edilir.

Bu job'lar secret, write permission, deployment environment veya external
service credential kullanmaz.

## Action Pinleri

Supply-chain değişkenliğini azaltmak için action major tag'leri yerine release
commit SHA değerleri kullanılır:

| Action | Release | Commit |
|---|---|---|
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | `v7.0.0` | `5fda3b95a4ea91299a34e894583c3862153e4b97` |

Yorumdaki release etiketi bakım sırasında SHA provenance değerinin kolayca
kontrol edilmesini sağlar.

Resmî release kaynakları:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [actions/setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0)

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

Bu aşamada `reports/ci` yalnızca job workspace'inde tutulur. Artifact upload
Backlog 5.4 kapsamında eklenecektir.

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
- İki action için tam 40 karakterli SHA ve release etiketi
- Python 3.11 ve pip cache yapılandırması
- Pip upgrade, dev install ve pytest komut sırası
- Ubuntu runner ve 10 dakikalık timeout
- Test job'una bağlı statik analiz job'u
- `src`, `tools` ve `sample_app` JSON rapor yolları
- Kontrollü demo exit code ve baseline doğrulaması

`tests/test_python_compatibility.py`, `src`, `sample_app`, `tools` ve `tests`
altındaki bütün Python dosyalarını desteklenen en düşük sürüm olan Python
3.11 grameriyle ayrıştırır. Böylece daha yeni bir yorumlayıcıda yerel olarak
geçen Python 3.12+ söz dizimi değişiklikleri CI'a ulaşmadan tespit edilir.

Doğrulanan mevcut sonuç:

```text
CI workflow contract tests: 10 passed
Python 3.11 compatibility tests: 1 passed
Complete test suite: 988 passed
Workflow YAML parse check: passed
```

## Sonraki Güvenlik Job'ları

Backlog 5.1 ve 5.2 tamamlanmıştır. Sonraki aşamalar:

1. Offline OSV fixture-backed dependency scan gate'i
2. Static ve dependency JSON raporlarını workflow artifact olarak yükleme

Bu ayrım her güvenlik gate'inin davranışını bağımsız olarak incelemeyi sağlar.

## Navigation

- [Proje dokümantasyonuna dön](README.md)
- [Tüm bileşenlere dön](components/README.md)
- [Projenin ana sayfasına dön](../README.md)
