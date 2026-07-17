import ast
from pathlib import Path


MAX_FUNCTION_LINES = 8


def analyze_file(file_path: Path) -> None:
    """Bir Python dosyasındaki uzun fonksiyonları tespit eder."""

    try:
        source_code = file_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Dosya okunamadı: {file_path}")
        print(f"Hata: {error}")
        return

    try:
        syntax_tree = ast.parse(source_code)
    except SyntaxError as error:
        print(
            f"Syntax hatası: {file_path}:{error.lineno} "
            f"{error.msg}"
        )
        return

    finding_count = 0

    for node in ast.walk(syntax_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start_line = node.lineno
            end_line = node.end_lineno or node.lineno
            function_length = end_line - start_line + 1

            if function_length > MAX_FUNCTION_LINES:
                finding_count += 1

                print(
                    f"[MEDIUM] {file_path}:{start_line} "
                    f"'{node.name}' fonksiyonu "
                    f"{function_length} satır uzunluğundadır."
                )

                print(
                    f"Öneri: Fonksiyonu {MAX_FUNCTION_LINES} "
                    "satırdan daha küçük parçalara ayırın."
                )

    if finding_count == 0:
        print("Uzun fonksiyon bulunamadı.")
    else:
        print(f"\nToplam bulgu: {finding_count}")


def main() -> None:
    target_file = Path("examples/vulnerable_code.py")

    if not target_file.exists():
        print(f"Dosya bulunamadı: {target_file}")
        return

    analyze_file(target_file)


if __name__ == "__main__":
    main()