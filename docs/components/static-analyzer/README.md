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

### SA002 — Long Class

Yapılandırılmış satır sınırını aşan Python sınıflarını tespit eder.

Varsayılan eşik:

```text
200 satır
```

Varsayılan önem seviyesi:

```text
WARNING
```

Örnek kullanım:

```python
import ast

from static_analyzer.rules import LongClassRule

source = """
class DataProcessor:
    first_value = 1
    second_value = 2
"""

tree = ast.parse(source)
rule = LongClassRule(max_lines=2)

findings = rule.check(tree, "example.py")
```

Kural aşağıdaki durumları destekler:

- Python sınıf tanımları
- İç içe sınıflar
- Yapılandırılabilir satır sınırı
- Aynı dosyada birden fazla bulgu
- Geçersiz eşik değerlerinin reddedilmesi

## Planlanan Kontroller

- Boş `except` bloğu tespiti
- `TODO` ve `FIXME` ifadelerinin tespiti
- Fonksiyon ve sınıf isimlendirme kontrolü
- Hardcoded parola, token veya anahtar tespiti

## Planlanan Girdiler

Araç tamamlandığında aşağıdaki girdileri kabul edecektir:

- Tek bir Python dosyasının yolu
- Python proje klasörünün yolu

Dosya ve klasör tarama mekanizması henüz geliştirilmemiştir.

Mevcut `LongFunctionRule`, doğrudan parse edilmiş bir `ast.AST` nesnesi ve
analiz edilen dosyanın yolunu kabul etmektedir.

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

Mevcut durumda toplam 24 test bulunmaktadır.

- 10 test `LongFunctionRule` davranışlarını doğrulamaktadır.
- 10 test `LongClassRule` davranışlarını doğrulamaktadır.
- 4 test ortak veri modeli ve temel kural arayüzünü doğrulamaktadır.

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
- `SA002` uzun sınıf kuralı
- Yapılandırılabilir sınıf uzunluğu sınırı
- İç içe sınıf desteği
- Geçersiz sınıf eşiği doğrulaması

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