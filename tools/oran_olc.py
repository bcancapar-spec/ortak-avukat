#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T13 (v0.5.9) — ORAN BEKÇİSİ ölçüm aracı (KAPI DEĞİL, yalnız ölçüm+defter).

Deterministik ölçüm:
  PAY   (mekanizma satırları) = plugins/**/scripts/*.py + tools/*.py
                                + hooks/* + plugins/**/hooks/*  — TEST HARİÇ
  PAYDA (öğreti satırları)    = plugins/**/*.md (SKILL + references + notlar)
  ORAN                        = pay / payda

AYRICA bilgi alanı (artışı iyidir, kapı yok): test/mekanizma oranı —
  TEST satırları = tests/**/*.py + pay adaylarından TEST diye dışlanan
  dosyalar (test_*.py / conftest.py).

Çıktı: stdout'a tek JSON {pay, payda, oran, test_satir,
test_mekanizma_orani, tarih, commit}. `--kaydet` verilirse ölçüm
`plugins/ortak-avukat/skills/ortak-avukat/references/oran-defteri.json`
append-only listesine EKLENİR (mevcut kayıtlar asla değiştirilmez/silinmez).

ANAYASA NOTU: oran için eşik/kapı KURULMAZ — o karar avukata (Can) aittir.
Bu araç yalnız gidişatı ölçülebilir kılar.
"""
import argparse
import datetime
import glob
import json
import os
import subprocess
import sys

DEFTER_GORELI = os.path.join("plugins", "ortak-avukat", "skills",
                             "ortak-avukat", "references", "oran-defteri.json")


def _test_dosyasi_mi(yol):
    """TEST HARİÇ kuralı: test_*.py / *_test.py / conftest.py veya yolunda
    tests / __pycache__ dizini geçen her dosya."""
    parcalar = [p.lower() for p in os.path.normpath(yol).split(os.sep)]
    ad = parcalar[-1]
    if ad.startswith("test_") or ad.endswith("_test.py") or ad == "conftest.py":
        return True
    return any(p in ("tests", "__pycache__") for p in parcalar[:-1])


def _satir_say(yol):
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def _dosyalar(kok, desenler):
    """Desenlerden tekil, sıralı DOSYA listesi (dizinler elenir)."""
    bulunan = set()
    for desen in desenler:
        for yol in glob.glob(os.path.join(kok, desen), recursive=True):
            if os.path.isfile(yol):
                bulunan.add(os.path.abspath(yol))
    return sorted(bulunan)


def _commit(kok):
    try:
        cikti = subprocess.run(
            ["git", "-C", kok, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10)
        if cikti.returncode == 0:
            return cikti.stdout.strip() or None
    except Exception:
        pass
    return None


def olc(kok):
    """Ölçümü yapar, sözlük döner. Deterministik: aynı ağaç → aynı sayılar
    (tarih/commit alanları hariç)."""
    kok = os.path.abspath(kok)
    pay_adaylari = _dosyalar(kok, [
        os.path.join("plugins", "**", "scripts", "*.py"),
        os.path.join("tools", "*.py"),
        os.path.join("hooks", "*"),
        os.path.join("plugins", "**", "hooks", "*"),
    ])
    pay = 0
    test_satir = 0
    for yol in pay_adaylari:
        if _test_dosyasi_mi(yol):
            test_satir += _satir_say(yol)     # TEST HARİÇ — bilgi alanına düşer
        else:
            pay += _satir_say(yol)
    for yol in _dosyalar(kok, [os.path.join("tests", "**", "*.py")]):
        if "__pycache__" not in yol:
            test_satir += _satir_say(yol)
    payda = sum(_satir_say(y)
                for y in _dosyalar(kok, [os.path.join("plugins", "**", "*.md")]))
    return {
        "pay": pay,
        "payda": payda,
        "oran": round(pay / payda, 4) if payda else None,
        "test_satir": test_satir,
        "test_mekanizma_orani": round(test_satir / pay, 4) if pay else None,
        "tarih": datetime.datetime.now().isoformat(timespec="seconds"),
        "commit": _commit(kok),
    }


def kaydet(kok, olcum):
    """Ölçümü append-only defter listesine EKLER; defter yolunu döner.
    Mevcut kayıtlar asla değiştirilmez — yalnız sona eklenir."""
    defter_yolu = os.path.join(os.path.abspath(kok), DEFTER_GORELI)
    kayitlar = []
    if os.path.isfile(defter_yolu):
        try:
            with open(defter_yolu, encoding="utf-8") as f:
                kayitlar = json.load(f)
        except Exception:
            kayitlar = []
        if not isinstance(kayitlar, list):
            kayitlar = [kayitlar]
    kayitlar.append(olcum)
    os.makedirs(os.path.dirname(defter_yolu), exist_ok=True)
    tmp = f"{defter_yolu}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, defter_yolu)
    return defter_yolu


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="oran bekçisi ölçümü — mekanizma/öğreti satır oranı "
                    "(kapı yok, yalnız ölçüm + append-only defter)")
    ap.add_argument("--kok", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))),
        help="ölçülecek ağaç kökü (varsayılan: bu deponun kökü)")
    ap.add_argument("--kaydet", action="store_true",
                    help="ölçümü references/oran-defteri.json'a EKLE (append-only)")
    args = ap.parse_args(argv)
    olcum = olc(args.kok)
    if args.kaydet:
        olcum["defter"] = os.path.relpath(kaydet(args.kok, olcum), args.kok)
    print(json.dumps(olcum, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
