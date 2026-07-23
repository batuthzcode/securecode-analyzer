# Static Code Analyzer

## Amaç

Python kaynak kodlarını çalıştırmadan inceleyerek temel kod kalitesi ve
güvenlik problemlerini tespit etmek.

## Kullanılan Yöntemler

- Python kodunun yapısal analizi için `ast`
- Metin tabanlı kontroller için satır taraması ve regex
- Otomatik testler için `pytest`

## Mevcut Analiz Kuralları

### SA001 — Long Function

Yapılandırılmış satır sınırını aşan normal ve asenkron fonksiyonları tespit
eder.

Varsayılan eşik:

```text
50 satır
```

Varsayılan önem seviyesi:

```text
WARNING
```

Örnek kullanım:

```python
import ast

from static_analyzer.rules import LongFunctionRule

source = """
def example_function():
    value_1 = 1
    value_2 = 2
"""

tree = ast.parse(source)
rule = LongFunctionRule(max_lines=2)

findings = rule.check(tree, "example.py")
```

Kural aşağıdaki durumları destekler:

- Normal fonksiyonlar
- Asenkron fonksiyonlar
- İç içe fonksiyonlar
- Yapılandırılabilir satır sınırı
- Aynı dosyada birden fazla bulgu

## Planlanan Kontroller

- Uzun sınıf tespiti
- Boş `except` bloğu tespiti
- `TODO` ve `FIXME` ifadelerinin tespiti
- Fonksiyon ve sınıf isimlendirme kontrolü
- Hardcoded parola, token veya anahtar tespiti

## Girdi

- Tek bir Python dosyası
- Python proje klasörü

Dosya ve klasör tarama mekanizması henüz geliştirilmemiştir. Mevcut kurallar
şu anda parse edilmiş AST nesneleri üzerinde çalışmaktadır.

## Çıktı

Her bulgu aşağıdaki bilgileri içerir:

- Kural kimliği
- Dosya yolu
- Satır numarası
- Varsa sütun numarası
- Önem seviyesi
- Problem açıklaması

## Test

Bütün testler aşağıdaki komutla çalıştırılır:

```bash
python -m pytest -v
```

Mevcut durumda toplam 14 test bulunmaktadır.

Bunların 10 tanesi `LongFunctionRule` davranışlarını doğrulamaktadır.

## Dokümantasyon

- [Analiz ve Gereksinimler](analysis.md)
- [Teknik Tasarım](technical-design.md)

## Mevcut Durum

Tamamlanan çalışmalar:

- Ortak `Finding` veri modeli
- `Severity` önem seviyeleri
- Soyut `BaseRule` arayüzü
- `SA001` uzun fonksiyon kuralı
- Yapılandırılabilir fonksiyon uzunluğu sınırı
- Normal ve asenkron fonksiyon desteği
- İç içe fonksiyon desteği
- Unit testler

Henüz tamamlanmayan çalışmalar:

- Dosya ve klasör tarama
- Analiz motoru
- CLI
- Terminal ve JSON raporlama
- Exit code yönetimi
- CI/CD entegrasyonu

## Navigation

- [Tüm bileşenlere dön](../README.md)
- [Projenin ana sayfasına dön](../../../README.md)