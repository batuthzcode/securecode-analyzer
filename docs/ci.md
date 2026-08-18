# GitHub Actions CI

Bu doküman Backlog 5.1 kapsamındaki temel test pipeline'ının gereksinimlerini,
güvenlik sınırlarını ve çalışma sırasını açıklar.

## Mevcut Durum

Temel GitHub Actions workflow'u tamamlanmıştır:

```text
.github/workflows/ci.yml
```

Workflow Pull Request değişikliklerinde ve `main` branch push olaylarında
Python 3.11 test paketini çalıştırır. Sıradaki aşama static analyzer,
dependency scanner ve report artifact adımlarının ayrı CI job'ları olarak
eklenmesidir.

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

Checkout sonrasında credential persistence kapalıdır. Test job'u
`ubuntu-latest` runner üzerinde en fazla 10 dakika çalışır. Aynı workflow ve
Git ref için yeni bir run başladığında önceki run iptal edilir.

Bu foundation job secret, write permission, deployment environment veya
external service credential kullanmaz.

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

## Yerel Eşdeğer

CI test adımını yerelde doğrulamak için:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
```

Workflow sözleşmesi de normal test paketi içindedir:

```powershell
python -m pytest tests/test_ci_workflow.py -q
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

Doğrulanan mevcut sonuç:

```text
CI workflow contract tests: 7 passed
Complete test suite: 984 passed
Workflow YAML parse check: passed
```

## Sonraki Güvenlik Job'ları

Bu foundation PR yalnızca Backlog 5.1'i tamamlar. Sonraki aşamalar:

1. `src` ve `tools` için sıfır-bulgu static self-analysis gate'i
2. `sample_app` için beklenen beş bulguyu drift testiyle doğrulama
3. Offline OSV fixture-backed dependency scan gate'i
4. Static ve dependency JSON raporlarını workflow artifact olarak yükleme

Bu ayrım temel test workflow'unun ilk gerçek GitHub run sonucunu bağımsız
olarak incelemeyi sağlar.

## Navigation

- [Proje dokümantasyonuna dön](README.md)
- [Tüm bileşenlere dön](components/README.md)
- [Projenin ana sayfasına dön](../README.md)
