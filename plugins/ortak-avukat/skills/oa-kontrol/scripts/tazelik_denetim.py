#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kontrol — tazelik_denetim.py  (v0.5.8, P6+P7 — graft deseninin devşirmesi;
bkz. anayasa m.0 dış desen devşirme protokolü, Can kararı 2026-08-12)

ÜRÜN-TAZELİK ZİNCİRİ: `_oa/cikti` ürünleri başlarındaki KAYNAK-BLOĞU ile
hangi girdiden türediklerini içerik-hash'iyle beyan eder (graft'ın
"Sources@hash" düğüm-başlığı deseni):

    <!-- kaynaklar: metin/00-kunye.json@a1b2c3d4 · cikti/01-illiyet-graf.json@e5f6a7b8 -->
    <!-- besledigi: 08-CBS-dilekce -->
    <!-- uretim: 2026-08-12T10:00Z · oa-strateji -->

Bu denetçi her ürünün beyan ettiği kaynak hash'lerini dosyaların BUGÜNKÜ
hash'iyle karşılaştırır; uyuşmayan ürün BAYAT ilan edilir ("kaynağı
üretiminden sonra değişti — delta geçişi gerek").

FELSEFE (amaç çizgisi): ADVISORY — her zaman exit 0. Saha kanıtı (Çal 1079):
graflar külliyatın %20'sindeyken doğdu, külliyat 5 kat büyüdü, ürünler
sessizce eskidi; delta emri İNSAN gözcüden geldi. Bu denetçi o gözcünün
otomasyonudur — BLOK değil, görünürlük. LLM'siz, token'sız, saniyelik.

Kullanım:
    python tazelik_denetim.py --kok <dava_koku> [--json]
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import hashlib
import json
import os
import re
import sys

KAYNAK_BLOK_RE = re.compile(
    r"<!--\s*kaynaklar:\s*(.+?)\s*-->", re.IGNORECASE)
# Girdi biçimi: "yol@sha8" öğeleri "·" veya "," ile ayrılır.
KAYNAK_OGE_RE = re.compile(r"(\S+?)@([0-9a-fA-F]{8})")


def sha8(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()[:8]


def _guvenli_yol(kok, goreli):
    """Kaynak yolu dava kökü İÇİNDE kalmalı (yol-kaçış koruması)."""
    tam = os.path.realpath(os.path.join(kok, "_oa", goreli))
    oa = os.path.realpath(os.path.join(kok, "_oa"))
    if not (tam == oa or tam.startswith(oa + os.sep)):
        return None
    return tam


def urun_denetle(kok, urun_yolu):
    """Tek ürünün kaynak-bloğunu okur; (bayatlar, eksikler) döndürür.
    Blok yoksa (None, None) — kademeli benimseme: bloksuz ürün denetim DIŞI."""
    with open(urun_yolu, encoding="utf-8", errors="replace") as f:
        bas = f.read(2048)  # blok dosyanın başındadır — bütünü okumaya gerek yok
    m = KAYNAK_BLOK_RE.search(bas)
    if not m:
        return None, None
    bayatlar, eksikler = [], []
    for goreli, beyan in KAYNAK_OGE_RE.findall(m.group(1)):
        tam = _guvenli_yol(kok, goreli)
        if tam is None or not os.path.isfile(tam):
            eksikler.append(goreli)
            continue
        simdiki = sha8(tam)
        if simdiki.lower() != beyan.lower():
            bayatlar.append((goreli, beyan.lower(), simdiki.lower()))
    return bayatlar, eksikler


def main():
    ap = argparse.ArgumentParser(
        description="Ürün-tazelik zinciri (v0.5.8 P6) — advisory, BLOKLAMAZ.")
    ap.add_argument("--kok", default=".", help="dava kökü (_oa'nın üstü)")
    ap.add_argument("--json", action="store_true",
                    help="DURUM.md advisory hattı için makine-okur çıktı")
    args = ap.parse_args()

    cikti = os.path.join(args.kok, "_oa", "cikti")
    if not os.path.isdir(cikti):
        if args.json:
            print(json.dumps({"durum": "cikti-yok", "bayat": [], "eksik": []},
                             ensure_ascii=False))
        else:
            print("tazelik: _oa/cikti yok — denetlenecek ürün bulunamadı.")
        sys.exit(0)

    rapor = {"bloklu": 0, "bloksuz": 0, "bayat": [], "eksik": []}
    for ad in sorted(os.listdir(cikti)):
        if not ad.endswith((".md", ".txt")):
            continue
        yol = os.path.join(cikti, ad)
        bayatlar, eksikler = urun_denetle(args.kok, yol)
        if bayatlar is None:
            rapor["bloksuz"] += 1
            continue
        rapor["bloklu"] += 1
        for goreli, beyan, simdiki in bayatlar:
            rapor["bayat"].append({"urun": ad, "kaynak": goreli,
                                   "beyan": beyan, "simdiki": simdiki})
        for goreli in eksikler:
            rapor["eksik"].append({"urun": ad, "kaynak": goreli})

    if args.json:
        print(json.dumps(rapor, ensure_ascii=False))
        sys.exit(0)

    print(f"tazelik: {rapor['bloklu']} bloklu ürün denetlendi "
          f"({rapor['bloksuz']} bloksuz — kademeli benimseme).")
    for b in rapor["bayat"]:
        print(f"  ⚠ BAYAT: {b['urun']} — kaynağı {b['kaynak']} üretiminden "
              f"sonra değişti ({b['beyan']} → {b['simdiki']}); delta geçişi gerek.")
    for e in rapor["eksik"]:
        print(f"  ⚠ EKSİK-KAYNAK: {e['urun']} — beyan edilen {e['kaynak']} "
              f"bulunamadı/kök dışında.")
    if not rapor["bayat"] and not rapor["eksik"]:
        print("  ✓ tüm bloklu ürünler TAZE.")
    sys.exit(0)  # advisory — her zaman 0 (amaç çizgisi: ateşlemeyen kapı yazma)


if __name__ == "__main__":
    main()
