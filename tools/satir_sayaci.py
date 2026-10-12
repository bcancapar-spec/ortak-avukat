# -*- coding: utf-8 -*-
"""Ortak Avukat — kod satırı sayacı (vitrin künyesinin ölçüm kaynağı).

NEDEN VAR: avukat talimatı (Av. Bayram Can ÇAPAR, 2026-10-07) — "kod satırlarının sayısını
da repoda başta belirt ki emek Claude ile yaptığımız ortaya çıksın". Vitrindeki her sayı
ölçümdür, beyan değil: sayı elle yazılmaz, bu araç git'te izlenen dosyalardan sayar.
README'ye AŞAĞI yuvarlanmış alt sınır yazılır (10.000 altı yüze, üstü bine: "900+",
"45.000+") — asla şişirilmez; test
sayısı tek kaynaktan (`tests/README.md` OA-SUIT-SAYISI, `test_b35` ile gerçek toplamaya
kilitli) tam yazılır. `tests/test_v0518_satir_sayaci.py` abartıyı ve bayatlığı kilitler.

Yöntem: `git ls-files -z` (izlenmeyen dosyalar — `_oa/` müvekkil evrakı, önbellekler,
worktree'ler — sayılmaz); utf-8 okuma (çözülemeyen bayt yerine U+FFFD),
`len(metin.splitlines())`, boş satırlar dahil. Ağ yok, depoya yalnız `--yaz` yazar.

Kullanım:
  python tools/satir_sayaci.py            # insan-okur özet
  python tools/satir_sayaci.py --json     # deterministik JSON (bayt-özdeş)
  python tools/satir_sayaci.py --yaz      # README'lerdeki işaretçili satırı tazeler
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
ISARETCI = "<!-- OA-SATIR-SAYACI -->"
README_LER = ("README.md", "plugins/ortak-avukat/README.md")
_SUIT_RE = re.compile(r"<!--\s*OA-SUIT-SAYISI:\s*(\d+)\s*-->")

# Sıra vitrindeki sırayla aynıdır (test kilitler): (anahtar, vitrin etiketi, süzgeç).
KATEGORILER = (
    ("eklenti_python", "eklenti kodu (Python)",
     lambda y: y.startswith("plugins/ortak-avukat/") and y.endswith(".py")),
    ("test_python", "test kodu",
     lambda y: y.startswith("tests/") and y.endswith(".py")),
    ("araclar", "araç kodu (tools/)",
     lambda y: y.startswith("tools/") and y.endswith((".py", ".ps1"))),
    ("beceri_metin", "beceri ve başvuru metni",
     lambda y: y.startswith("plugins/ortak-avukat/") and y.endswith(".md")),
    ("kural_veri", "kural ve veri (JSON)",
     lambda y: y.startswith("plugins/ortak-avukat/") and y.endswith(".json")),
)


def izlenen_dosyalar(kok=KOK):
    cp = subprocess.run(["git", "-C", str(kok), "ls-files", "-z"], capture_output=True, check=True)
    return sorted(y for y in cp.stdout.decode("utf-8").split("\0") if y)


def satir_say(yol):
    return len(yol.read_bytes().decode("utf-8", "replace").splitlines())


def test_sayisi(kok=KOK):
    m = _SUIT_RE.search((kok / "tests" / "README.md").read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("HATA: tests/README.md'de OA-SUIT-SAYISI işaretçisi yok")
    return int(m.group(1))


def say(kok=KOK):
    dosyalar = izlenen_dosyalar(kok)
    kategoriler = {}
    for ad, _etiket, suzgec in KATEGORILER:
        # İndekste olup diskte olmayan (silinmiş, sahnelenmemiş) dosya sayılmaz.
        secili = [kok / y for y in dosyalar if suzgec(y) and (kok / y).is_file()]
        kategoriler[ad] = {"dosya": len(secili), "satir": sum(satir_say(p) for p in secili)}
    toplam = {"dosya": sum(k["dosya"] for k in kategoriler.values()),
              "satir": sum(k["satir"] for k in kategoriler.values())}
    return {"kategoriler": kategoriler, "toplam": toplam, "test_sayisi": test_sayisi(kok)}


def alt_sinir(n):
    """Aşağı yuvarlanmış alt sınır: 10.000 altı yüze, üstü bine (963 → 900, 45.937 → 45.000).
    Küçük kategori "0+" görünmesin, büyük sayı gereksiz kesinlik taşımasın diye iki basamaklı."""
    n = int(n)
    adim = 100 if n < 10000 else 1000
    return (n // adim) * adim


def tr_sayi(n):
    return f"{int(n):,}".replace(",", ".")


def ifade(n):
    return tr_sayi(alt_sinir(n)) + "+"


def satir_metni(olcum):
    k = olcum["kategoriler"]
    parcalar = [f"**{ifade(k[ad]['satir'])}** satır {etiket}" for ad, etiket, _ in KATEGORILER]
    return ("**Birlikte yazılan:** " + " · ".join(parcalar)
            + f" · toplam **{ifade(olcum['toplam']['satir'])}** satır"
            + f" · **{tr_sayi(olcum['test_sayisi'])}** test"
            + " — ölçüm: `python tools/satir_sayaci.py` (git'te izlenen dosyalar, boş satırlar"
            + " dahil; satır sayıları aşağı yuvarlanmış alt sınırdır) " + ISARETCI)


def tazele(metin, olcum):
    """Yalnız işaretçili satırın içeriğini yeniler; satır sonu (CRLF/LF) korunur. İdempotent."""
    yeni = []
    for s in metin.splitlines(True):
        if ISARETCI in s:
            s = satir_metni(olcum) + s[len(s.rstrip("\r\n")):]
        yeni.append(s)
    return "".join(yeni)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Ortak Avukat kod satırı sayacı (vitrin künyesinin ölçüm kaynağı)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true", help="deterministik JSON bas")
    g.add_argument("--yaz", action="store_true", help="README'lerdeki işaretçili satırı tazele")
    a = ap.parse_args(argv)
    olcum = say()
    if a.json:
        veri = dict(olcum, yontem={"kaynak": "git ls-files -z", "bos_satirlar_dahil": True, "kodlama": "utf-8"})
        sys.stdout.flush()
        sys.stdout.buffer.write((json.dumps(veri, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return 0
    if a.yaz:
        for ad in README_LER:
            yol = KOK / ad
            eski = yol.read_bytes().decode("utf-8")
            if eski.count(ISARETCI) != 1:
                print(f"HATA: {ad}: işaretçi satırı tam bir kez olmalı (bulunan {eski.count(ISARETCI)})",
                      file=sys.stderr)
                return 1
            yeni = tazele(eski, olcum)
            if yeni != eski:
                yol.write_bytes(yeni.encode("utf-8"))
                print(f"tazelendi: {ad}")
            else:
                print(f"güncel: {ad}")
        return 0
    for ad, etiket, _ in KATEGORILER:
        k = olcum["kategoriler"][ad]
        print(f"{etiket:<28} {k['dosya']:>5} dosya  {tr_sayi(k['satir']):>9} satır")
    t = olcum["toplam"]
    print(f"{'toplam':<28} {t['dosya']:>5} dosya  {tr_sayi(t['satir']):>9} satır")
    print(f"test sayısı (OA-SUIT-SAYISI): {tr_sayi(olcum['test_sayisi'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
