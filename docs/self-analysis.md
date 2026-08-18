# Whole-Project Self-Analysis and Test Coverage

Bu belge Backlog 5.5 kapsamındaki eksik test denetimini ve statik analiz
aracının kendi repository'si üzerinde çalıştırılmasının sonuçlarını kaydeder.

## Sonuç

Production static analyzer `src`, `sample_app`, `tools` ve `tests` dahil bütün
Python kaynaklarında çalıştırılmıştır. Son canonical rapor:

```text
reports/project/static-analysis.json
```

Rapor yalnızca `sample_app/analyzer_demo.py` içindeki beş kontrollü örneği
içerir. Çalışan Flask uygulaması bu modülü import etmez; bulgular aracın demo
çıktısını göstermek için bilinçli olarak tutulan gerçek pozitiflerdir.

| Rule | Konum | Sınıflandırma |
|---|---|---|
| `SA005` | `analyzer_demo.py:8` | Kontrollü hardcoded-secret örneği |
| `SA001` | `analyzer_demo.py:11` | Kontrollü long-function örneği |
| `SA006` | `analyzer_demo.py:11` | Kontrollü naming örneği |
| `SA003` | `analyzer_demo.py:14` | Kontrollü TODO örneği |
| `SA004` | `analyzer_demo.py:54` | Kontrollü empty-except örneği |

Final raporda bilinen false positive yoktur. Beş bulgunun tümü beklenen ve
testlerle tam konumuna kadar sabitlenmiş true positive demo fixture'larıdır.

## İlk Tarama ve Düzeltmeler

İlk repository taraması 10 bulgu üretti. Beş demo bulgusuna ek olarak dört
test fonksiyonu `SA001` sınırını aşıyor, bir hardcoded-secret kural testi de
test verisini kendi kaynak kodunda literal olarak tuttuğu için `SA005`
üretiyordu.

Uygulanan düzeltmeler:

- Uzun subprocess kurulum kodu küçük ve isimlendirilmiş helper'lara ayrıldı.
- Büyük OSV payload'ları test fonksiyonlarından module-level fixture
  sabitlerine taşındı.
- Demo finding beklentisi tek bir okunabilir sabitte toplandı.
- Secret redaction testi aynı değeri runtime'da parçalardan kuracak şekilde
  değiştirildi; üretim analyzer'ına verilen kaynak hâlâ literal secret
  assignment içerdiğinden kural davranışı korunuyor.

Bu değişikliklerden sonra uygulama, araç ve test kaynaklarında beklenmeyen
bulgu kalmadı.

## Test Kapsamı

Coverage ölçümü statement ve branch kapsamını birlikte hesaplar:

```toml
[tool.coverage.run]
branch = true
source = ["src", "sample_app", "tools"]
omit = ["*/sample_app/analyzer_demo.py"]
```

`analyzer_demo.py` bilerek güvenli olmayan kaynak örnekleri içerdiği ve hiçbir
zaman import edilmemesi gerektiği için runtime coverage paydasından çıkarılır.
Dosya static-analysis ve integration test kapsamından çıkarılmaz.

İlk ölçümde demo hariç birleşik kapsam yaklaşık `%95,4` idi. Eksik dallara
eklenen testlerden sonra doğrulanan sonuç:

```text
Tests: 1065 passed
Combined statement/branch coverage: 98.6%
Required CI floor: 97.0%
```

Eklenen veya tamamlanan sözleşmeler:

- OSV direct network error, timeout, status ve response-body hataları
- Offline fixture JSON, metadata, query ve parser hataları
- Dependency model type doğrulaması
- CVSS privilege/scope ağırlıklarının bütün dalları
- CLI operational exit code `2` ve report normalization hataları
- JSON report missing, stale, current ve write modları
- Hardcoded-secret deduplication ve unsupported AST target davranışı
- Whole-project rapor üretimi, drift kontrolü ve portable yollar
- Kontrollü demo bulgularının tam rule, dosya, satır ve severity eşleşmesi

Kapsam dışında kalan az sayıdaki satır; abstract base guard'ları, argparse
choices sonrasındaki erişilemeyen defensive error'lar, Flask/Werkzeug'ün tip
garantisi verdiği form dalları ve yalnızca module entrypoint süreçlerinde
çalışan `__main__` guard'larıdır. Bunlar public davranış yerine interpreter veya
framework sözleşmesini tekrar eden yapay testler gerektirdiği için coverage
hedefi `%100` olarak belirlenmemiştir.

## Yeniden Üretim

PowerShell üzerinde tam test ve coverage gate'i:

```powershell
python -m coverage run -m pytest -q
python -m coverage report
```

Canonical self-analysis raporunu üretmek için:

```powershell
python -m tools.generate_self_analysis_report
```

Dosya yazmadan drift kontrolü yapmak için:

```powershell
python -m tools.generate_self_analysis_report --check
```

`--check`, rapor eksik veya güncel değilse exit code `1`; exact match için
exit code `0` döndürür. CI hem `%97` coverage floor'unu hem de canonical
self-analysis raporunu her Pull Request'te doğrular.

## Navigation

- [GitHub Actions CI](ci.md)
- [Beş Haftalık Proje Planı](project-plan.md)
- [Proje dokümantasyonuna dön](README.md)
- [Projenin ana sayfasına dön](../README.md)
