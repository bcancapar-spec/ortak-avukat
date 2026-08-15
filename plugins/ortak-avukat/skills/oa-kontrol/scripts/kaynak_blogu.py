#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kontrol — kaynak_blogu.py  (v0.5.8.4 — KAYNAK-BLOĞU ÜRETİCİSİ)

372 Torbalı saha bulgusu: KAYNAK-BLOĞU deseni (graft "Sources@hash") sahada
YARIM kaldı — model blokları yazdı ama @sha8'siz; `tazelik_denetim.py`'nin
KAYNAK_OGE_RE'si hash'siz öğeyi yakalamadığından ürün-tazelik denetimi fiilen
İŞLEVSİZDİ. Modelden elle sha256 hesaplaması beklenemez (deterministik iş
script'in işidir — model kurar / script denetler ayrımı). Bu üretici, bloğu
`tazelik_denetim.py`'nin regexleriyle (KAYNAK_BLOK_RE + KAYNAK_OGE_RE)
BİREBİR eşleşecek biçimde TEK SATIR olarak stdout'a basar:

    <!-- kaynaklar: metin/00-kunye.json@a1b2c3d4 · cikti/01-graf.json@e5f6a7b8 | besledigi: 08-dilekce | uretim: 2026-08-15T10:00Z -->

Sözleşme (round-trip garantisi — testte tazelik_denetim İMPORT edilerek
doğrulanır):
  • sha8 = dosya HAM BAYTLARININ sha256'sının ilk 8 hex'i
    (tazelik_denetim.sha8 ile aynı algoritma — orası denetler, burası üretir);
  • öğe ayırıcı " · " (KAYNAK_OGE_RE zaten "·"/"," kabul eder);
  • dosya yoksa öğe 'yol@BULUNAMADI' yazılır + stderr'e uyarı düşer, exit 0
    (üretici BLOKLAMAZ; hash'siz öğeyi dilekce_denetim'in istişari
    KAYNAK-BLOĞU uyarısı zaten görünür kılar);
  • yol ayracı "/"ye çevrilir (Windows'ta üretilen blok ubuntu-CI'da ve
    tazelik_denetim'in os.path.join çözümünde aynı şekilde çalışır).

Kullanım:
    python kaynak_blogu.py --girdiler yol1 yol2 ... [--besledigi X] [--uretim Y]

Çıkış kodu: HER DURUMDA 0 (amaç çizgisi: üretici araç kapı değildir).
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
import os
import re
import sys


def sha8(yol):
    """Dosya ham baytlarının sha256 ilk 8 hex'i — tazelik_denetim.sha8 ile
    BİREBİR aynı algoritma (üretici/denetçi simetrisi)."""
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()[:8]


def _oge_uret(yol):
    """Tek girdi yolu → ('yol@sha8' | 'yol@BULUNAMADI', uyarı|None).
    Yol ayracı '/'ye çevrilir; boşluklu yol KAYNAK_OGE_RE'nin \\S+ desenine
    takılacağından GÖRÜNÜR uyarı düşülür (sessiz uyumsuzluk yok)."""
    goreli = yol.replace(os.sep, "/").replace("\\", "/")
    uyari = None
    if re.search(r"\s", goreli):
        uyari = ("UYARI: '%s' boşluk içeriyor — tazelik_denetim.KAYNAK_OGE_RE "
                 "(\\S+@sha8) bu öğeyi TAM yakalayamaz; yolu boşluksuz kurun." % goreli)
    if not os.path.isfile(yol):
        eksik = ("UYARI: '%s' bulunamadı — öğe '@BULUNAMADI' yazıldı; "
                 "tazelik_denetim bu ürünü hash'siz öğeyle denetleyemez." % yol)
        return goreli + "@BULUNAMADI", (uyari + "\n" + eksik if uyari else eksik)
    return goreli + "@" + sha8(yol), uyari


def blok_uret(girdiler, besledigi=None, uretim=None):
    """(tek_satir_blok, uyarılar) döndürür. Satır, tazelik_denetim'in
    KAYNAK_BLOK_RE'siyle eşleşir; öğeler KAYNAK_OGE_RE ile ayrıştırılır."""
    ogeler, uyarilar = [], []
    for yol in girdiler:
        oge, uyari = _oge_uret(yol)
        ogeler.append(oge)
        if uyari:
            uyarilar.append(uyari)
    parcalar = ["kaynaklar: " + " · ".join(ogeler)]
    if besledigi:
        parcalar.append("besledigi: " + besledigi)
    if uretim:
        parcalar.append("uretim: " + uretim)
    return "<!-- " + " | ".join(parcalar) + " -->", uyarilar


def main():
    ap = argparse.ArgumentParser(
        description="KAYNAK-BLOĞU üreticisi (v0.5.8.4) — tazelik_denetim.py'nin "
                    "denetleyebildiği '<!-- kaynaklar: yol@sha8 ... -->' satırını basar.")
    ap.add_argument("--girdiler", nargs="+", required=True, metavar="YOL",
                    help="Ürünün türediği girdi dosyaları (tazelik_denetim "
                         "çözümüyle uyum için dava kökündeki _oa/ altına GÖRELİ verin).")
    ap.add_argument("--besledigi", default=None, metavar="X",
                    help="(opsiyonel) ürünün beslediği sonraki halka (ör. 08-dilekce).")
    ap.add_argument("--uretim", default=None, metavar="Y",
                    help="(opsiyonel) üretim damgası (ör. 2026-08-15T10:00Z · oa-strateji).")
    a = ap.parse_args()

    satir, uyarilar = blok_uret(a.girdiler, a.besledigi, a.uretim)
    for u in uyarilar:
        print(u, file=sys.stderr)
    print(satir)
    sys.exit(0)  # üretici araç kapı DEĞİLDİR — her durumda 0


if __name__ == "__main__":
    main()
