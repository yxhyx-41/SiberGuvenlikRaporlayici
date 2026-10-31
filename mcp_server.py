"""SiberGuvenlikRaporlayici MCP Server.

Guncel MCP Python SDK v2 (MCPServer) kullanir.

Gui sahiptir:
  - hello(name)                 : selamlama
  - list_files(directory)       : klasordeki dosyalari listeler (alt klasorlere inmez)
  - read_log(path, tail)        : log dosyasinin son N satirini maskelenmis sekilde okur
  - calculate_hash(file, algo)  : dosyanin hash degerini hesaplar (yazma yapmaz)

Guvenlik:
  - Tum dosya erisimi proje katalogu ile sinirlidir (path traversal engellenir).
  - Yukarida listelenen hassas desenler log cikisunda maskelenir.
  - read_log tail degeri sinirlidir; zorunlu satir sonu uygulanir.
  - calculate_hash yalnizca onayli algoritmalari destekler ve dosyayi sadece okur.
"""

from pathlib import Path
import hashlib
import logging
import re

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logger = logging.getLogger("siber-mcp")

mcp = MCPServer("SiberGuvenlikRaporlayici")

# Tum dosya erisimi bu katalogla sinirlidir.
PROJECT_ROOT = Path(__file__).resolve().parent

# read_log icin okunacak maksimum satir (gerekli olmayan buyuk okumalar engellensin).
MAX_TAIL_LINES = 5000
DEFAULT_TAIL_LINES = 100

# calculate_hash icin desteklenen algoritmalar.
SUPPORTED_HASH_ALGORITHMS = ("sha256", "sha1", "md5")

# read_log cikisinda maskelenecek hassas degerler.
_SENSITIVE_PATTERNS = re.compile(
    r"(?i)(password|passwd|pwd|token|api[_-]?key|secret|auth|authorization|"
    r"access[_-]?key|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*[^\s,;]+"
    r"|\bbearer\s+[a-z0-9._~+/=-]+"
    r"|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def _resolve_allowed(path_str: str) -> Path:
    """Verilen yolu proje katalogu icinde cozer; disari cikisini/cikimi engeller.

    - '..' / path traversal parcasi olan her giris burada durdurulur.
    - Mutlak ve goreli yollar desteklenir; sonuc her zaman PROJECT_ROOT icinde olmalidir.
    """
    path = Path(path_str)

    # Go bakalim null byte gibi tehlikeli girdiler.
    if "\x00" in path_str:
        raise ToolError("Gecersiz yol: null byte iceriyor.")

    if not path.is_absolute():
        resolved = (PROJECT_ROOT / path).resolve()
    else:
        resolved = path.resolve()

    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ToolError(
            f"Erisim engellendi: '{path_str}' proje katalogu disina cikiyor."
        ) from None

    return resolved


def _mask_sensitive(text: str) -> str:
    """Log metnindeki hassas degerleri maskeler."""
    def _redact(match: re.Match) -> str:
        matched = match.group(0)
        if "@" in matched:
            return "<REDACTED>"
        return matched.split("=", 1)[0] + "=<REDACTED>"

    return _SENSITIVE_PATTERNS.sub(_redact, text)


@mcp.tool()
def hello(name: str) -> str:
    """Bir kullaniciyi adiyla selamlar."""
    return f"Merhaba {name}!"


@mcp.tool()
def list_files(directory: str = ".") -> str:
    """Belirtilen klasordeki dosya ve alt klasorleri listeler.

    Alt klasorlere otomatik girilmez. Dosyalar icin boyut, dizinler icin '<DIR>'
    olarak gosterilir. Erisim yalnizca proje katalogu icindeki konumlara izinlidir.
    """
    target = _resolve_allowed(directory)

    if not target.exists():
        raise ToolError(f"Klasor bulunamadi: '{directory}'")
    if not target.is_dir():
        raise ToolError(f"Belirtilen konum bir klasor degil: '{directory}'")

    entries = []
    try:
        for child in sorted(target.iterdir()):
            if child.is_dir():
                entries.append(f"[DIR]  {child.name}")
            else:
                try:
                    size = child.stat().st_size
                except OSError:
                    size = -1
                entries.append(f"{size:>10}  {child.name}")
    except OSError as exc:
        raise ToolError(f"Klasor okunamadi: {exc}") from exc

    return (
        f"Klasor: {target} ({len(entries)} ogeler)\n"
        + ("\n".join(entries) if entries else "(bos)")
    )


@mcp.tool()
def read_log(log_path: str, tail: int = DEFAULT_TAIL_LINES) -> str:
    """Belirtilen log dosyasinin son 'tail' satirini okur.

    Varsayilan deger 100'tur ve en fazla 5000 satir okunur. Yalnizca proje
    katalogu icindeki dosyalara erisilir. Parola, token, API anahtari ve e-posta
    gibi hassas icerikler rapora gecirilmeden maskelenir.
    """
    # tail sinirla (gerekli olmayan buyuk okumalari onler).
    if tail <= 0:
        raise ToolError("tail pozitif bir tam sayi olmalidir.")
    lines_to_read = min(tail, MAX_TAIL_LINES)

    target = _resolve_allowed(log_path)

    if not target.exists():
        raise ToolError(f"Dosya bulunamadi: '{log_path}'")
    if not target.is_file():
        raise ToolError(f"Belirtilen konum bir dosya degil: '{log_path}'")

    try:
        with open(target, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        raise ToolError(f"Log dosyasi okunamadi: {exc}") from exc

    last_lines = lines[-lines_to_read:]
    safe_lines = [_mask_sensitive(line.rstrip("\n")) for line in last_lines]

    return (
        f"Dosya: {target} | Okunan satir: {len(safe_lines)} | Toplam satir: {len(lines)}\n"
        + ("\n".join(safe_lines) if safe_lines else "(bos)")
    )


@mcp.tool()
def calculate_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Belirtilen dosyanin hash degerini hesaplar.

    Varsayilan algoritma SHA-256 icindir; desteklenen diger degerler: sha1, md5.
    Bu tool dosyayi yalnizca okur, asla degistirmez. Erisim yalnizca proje
    katalogu icindeki dosyalara izinlidir.
    """
    algo = algorithm.lower()
    if algo not in SUPPORTED_HASH_ALGORITHMS:
        raise ToolError(
            f"Desteklenmeyen algoritma: '{algorithm}'. "
            f"Desteklenenler: {', '.join(SUPPORTED_HASH_ALGORITHMS)}"
        )

    target = _resolve_allowed(file_path)

    if not target.exists():
        raise ToolError(f"Dosya bulunamadi: '{file_path}'")
    if not target.is_file():
        raise ToolError(f"Belirtilen konum bir dosya degil: '{file_path}'")

    hasher = hashlib.new(algo)
    try:
        with open(target, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                hasher.update(chunk)
    except OSError as exc:
        raise ToolError(f"Dosya okunamadi: {exc}") from exc

    return f"{algo}:{hasher.hexdigest()}"


if __name__ == "__main__":
    mcp.run()